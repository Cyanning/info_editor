import json
import sqlite3
from model.bodymodel import *
from configuration import *


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
    cur.execute("SELECT text_hash FROM ia_connect WHERE model_value=%d ORDER BY order_id" % value)
    sentence_hashes = [x[0] for x in cur.fetchall()]
    sentences = []
    for sentence_hash in sentence_hashes:
        cur.execute("SELECT context FROM attribution WHERE text_hash='%s'" % sentence_hash)
        try:
            sentences.append(cur.fetchone()[0])
        except (TypeError, IndexError):
            continue
    model = BodyModel(value, name, sentences)
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
    根据关键词和系统限定，搜索并生成模型，无句子信息
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
    cur.execute("SELECT text_hash FROM ia_connect WHERE model_value=%d ORDER BY order_id" % value)
    for thash in (x[0] for x in cur.fetchall()):
        cur.execute("SELECT context FROM attribution WHERE text_hash='%s'" % thash)
        try:
            yield Sentence(cur.fetchone()[0])
        except (TypeError, IndexError):
            continue
    db.close()


def saving_model_basedon_paragraph(model: BodyModel):
    try:
        model.convert_into_sentences()
    except AssertionError:
        # 依据断言判断出为空白内容, 删除所有句子
        model.clean_sentences()
    saving_model(model)


def saving_model(body: BodyModel):
    """
    保存一个模型的所有关系
    """
    db, cur = open_database()
    # 读取已存在的关系
    cur.execute("SELECT text_hash FROM ia_connect WHERE model_value=%d ORDER BY order_id" % body.value)
    hash_exists = [x[0] for x in cur.fetchall()]
    idxes_excluded = set()

    # 循环存储每个句子
    for idx_now, sentence in enumerate(body):
        hash_now = sentence.gethash
        # 判断关系是否已存在
        if hash_now in hash_exists:
            idx_exists = hash_exists.index(hash_now)
            # 如果顺序有变动则更改序号
            if idx_exists != idx_now:
                cur.execute(
                    "UPDATE ia_connect SET order_id=? WHERE model_value=? AND text_hash=?",
                    (idx_now, body.value, hash_now)
                )
            # 记录需要保留的已存在句子
            idxes_excluded.add(idx_exists)
            continue
        # 判断句子是否存在, 不存在就存句子
        cur.execute("SELECT COUNT(*) FROM attribution WHERE text_hash='%s'" % hash_now)
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO attribution (context,text_hash) VALUES (?,?)", (sentence.value, hash_now))
        # 存关系
        cur.execute(
            "INSERT INTO ia_connect (model_value,text_hash,order_id) VALUES (?,?,?)", (body.value, hash_now, idx_now)
        )

    # 删除无关联的句子关系
    cur.executemany(
        "DELETE FROM ia_connect WHERE model_value=? AND text_hash=?",
        ((body.value, hash_) for i, hash_ in enumerate(hash_exists) if i not in idxes_excluded)
    )
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


def export_database_json(target_path):
    """
    把数据库数据导出为json文件
    """
    db, cur = open_database()
    cur.execute("SELECT text_hash,context FROM attribution")
    _attribution = [{"text_hash": row[0], "context": row[1]} for row in cur.fetchall()]

    cur.execute("SELECT text_hash,model_value,order_id FROM ia_connect")
    _ia_connect = [{"text_hash": row[0], "model_value": row[1], "order_id": row[2]} for row in cur.fetchall()]

    for name, jsonobj in zip(["attribution", "ia_connect"], [_attribution, _ia_connect]):
        jsonstr = json.dumps(jsonobj, ensure_ascii=False)
        with open(f"{target_path}/{name}.json", 'w', encoding='UTF-8') as f:
            f.write(jsonstr)


def export_database_of_system_json(target_path, sysid):
    """
    把数据库数据导出为json文件, 分系统
    """
    db, cur = open_database()
    cur.execute("SELECT value FROM info WHERE sysid=%d" % sysid)
    values = (x[0] for x in cur.fetchall())
    cur.execute(
        f"SELECT text_hash,model_value,order_id FROM ia_connect WHERE model_value in ({','.join(map(str, values))})"
    )
    _ia_connect = [{"text_hash": row[0], "model_value": row[1], "order_id": row[2]} for row in cur.fetchall()]

    _text_hash = set(x['text_hash'] for x in _ia_connect)
    cur.execute(f"SELECT text_hash,context FROM attribution WHERE text_hash in ({','.join(_text_hash)})")
    _attribution = [{"text_hash": row[0], "context": row[1]} for row in cur.fetchall()]

    for name, jsonobj in zip(["attribution", "ia_connect"], [_attribution, _ia_connect]):
        jsonstr = json.dumps(jsonobj, ensure_ascii=False)
        with open(f"{target_path}/{name}.json", 'w', encoding='UTF-8') as f:
            f.write(jsonstr)


def percentage_of_progress_completed(gender, sysid) -> int:
    """
    搜索某系统完成的百分比
    :param gender: 0 or 1
    :param sysid: -1 为全部
    :return: 百分比的整数部分
    """
    db, cur = open_database()
    attach = f" AND sysid={sysid}" if sysid == -1 else ""
    cur.execute(f"SELECT value FROM info WHERE sex={gender}" + attach)
    values = [str(x) for x in cur.fetchall()]
    cur.execute(f"SELECT COUNT(DISTINCT model_value) FROM ia_connect WHERE model_value IN ({','.join(values)})")
    number = cur.fetchone()[0]

    percentage = int(number / len(values) * 100)
    if percentage > 100:
        percentage = 100
    return percentage
