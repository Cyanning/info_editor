import json
import sqlite3
from model.bodymodel import *
from configuration import *


SYSTEMS = ['全部', '骨骼', '结缔', '肌肉', '动脉', '静脉', '淋巴', '神经', '呼吸', '消化', '内分泌', '泌尿生殖', '皮肤']


def write_cache_model(num: int):
    """写退出时的模型id"""
    with open(RTPATH + "cache/periousValue.dll", 'w', encoding='UTF-8') as w:
        w.write(str(num))


def load_cache_model() -> BodyModel:
    """读退出时的模型id"""
    try:
        with open(RTPATH + "cache/periousValue.dll", 'r', encoding='UTF-8') as f:
            strings = f.read().strip()
            value = int(strings)
            return create_by_value(value)
    except FileNotFoundError:
        return create_next_value(100000, 0)


def open_database():
    database = sqlite3.connect(RTPATH + "cache/creature.db")
    return database, database.cursor()


def create_by_value(value: int) -> BodyModel:
    """
    基于id创建模型，附带原info信息
    """
    db, cur = open_database()
    cur.execute("SELECT name FROM info WHERE value=%d" % value)
    res = cur.fetchone()
    assert res is not None
    name = res[0]
    cur.execute("SELECT context FROM attribution WHERE text_hash IN ("
                "SELECT text_hash FROM ia_connect WHERE model_value=%d)" % value)
    model = BodyModel(value, name, (x[0] for x in cur.fetchall()))
    db.close()
    return model


def create_next_value(value: int, direction: int) -> BodyModel:
    """
    生成上一个、下一个、首个、限定系统内的首个模型
    :param value: 起始/目标
    :param direction: 前进 +1；后退 -1；跳转 0
    """
    assert 100000 <= value < 212000 or 1000000 <= value < 2120000
    db, cur = open_database()
    cur.execute(f"SELECT value FROM info ORDER BY sysid,value")
    values = [x[0] for x in cur.fetchall()]
    db.close()
    try:
        idx = values.index(value) + direction
        idx %= len(values)
    except ValueError:
        # 如果传入的value不在数据库里面，则跳转到与此value最接近的value（距离相同取后一位）
        values.sort()  # 先整理为纯大小排序
        maxidx = len(values)
        minidx = 0
        while maxidx - minidx > 1:
            mididx = (maxidx - minidx) // 2 + minidx
            if values[mididx] > value:
                maxidx = mididx
            else:
                minidx = mididx
        idx = minidx if value - values[minidx] < values[maxidx] - value else maxidx
    return create_by_value(values[idx])


def produce_by_search(kws: str, sysid: int | None) -> BodyModel:
    """
    根据关键词和系统限定，搜索并生成模型
    """
    db, cur = open_database()
    sys_sql = '' if sysid is None else f" AND sysid={sysid}"
    cur.execute("SELECT value,name FROM info WHERE ("
                f"name LIKE '%{kws}%' OR info LIKE '%{kws}%' OR value LIKE '%{kws}%'){sys_sql}")
    for val, name in cur.fetchall():
        yield BodyModel(val, name, [])
    db.close()


def produce_sentences_by_value(value: int) -> list[Sentence]:
    """
    基于模型vlaue载入所有关联的句子
    """
    db, cur = open_database()
    cur.execute("SELECT context FROM attribution WHERE text_hash IN ("
                "SELECT text_hash FROM ia_connect WHERE model_value=%d)" % value)
    for row in cur.fetchall():
        yield Sentence(row[0])
    db.close()


def saving_model_basedon_paragraph(model: BodyModel):
    try:
        model.convert_into_sentences()
    except AssertionError:
        # 依据断言判断出为空白内容, 删除所有关系
        model.clean_sentences()
    saving_model(model)


def saving_model(model: BodyModel):
    """
    保存一个模型的所有关系
    """
    db, cur = open_database()
    try:
        assert len(model) > 0
        # 读取已存在的关系
        cur.execute("SELECT text_hash FROM ia_connect WHERE model_value=%d" % model.value)
        sentence_exists = [x[0] for x in cur.fetchall()]
        # 循环存储
        for sentence in model:
            hashtext = sentence.gethash
            if hashtext in sentence_exists:
                # 判断是否需要新加关系
                sentence_exists.remove(hashtext)
                continue
            # 先判断句子存不存在，再存句子
            cur.execute("SELECT COUNT(*) FROM attribution WHERE text_hash='%s'" % hashtext)
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO attribution (context,text_hash) VALUES (?,?)", (sentence.value, hashtext))
            # 存关系
            cur.execute("INSERT INTO ia_connect (model_value,text_hash) VALUES (?,?)", (model.value, hashtext))

        # 删除已存在关系中剩余的无用关系
        cur.executemany(
            "DELETE FROM ia_connect WHERE model_value=? AND text_hash=?", ((model.value, x) for x in sentence_exists)
        )
    except AssertionError:
        cur.execute("DELETE FROM ia_connect WHERE model_value=%d" % model.value)
    finally:
        db.commit()
        db.close()


def get_old_info(value: int) -> str:
    """
    获取老版本信息
    """
    db, cur = open_database()
    cur.execute("SELECT info FROM info WHERE value=%d" % value)
    context = cur.fetchone()

    assert context is not None
    context = context[0]

    assert context is not None
    context.strip()
    return context


def export_database_to_json(target_path):
    """
    把数据库数据导出为json文件
    """
    db, cur = open_database()
    cur.execute("SELECT text_hash,context FROM attribution")
    data = {"attribution": [{"text_hash": row[0], "context": row[1]} for row in cur.fetchall()]}

    cur.execute("SELECT text_hash,model_value FROM ia_connect")
    data["ia_connect"] = [{"text_hash": row[0], "model_value": row[1]} for row in cur.fetchall()]

    for name, jsonobj in data.items():
        jsonstr = json.dumps(jsonobj, ensure_ascii=False)
        with open(f"{target_path}/{name}.json", 'w', encoding='UTF-8') as f:
            f.write(jsonstr)
