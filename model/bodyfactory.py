import json
import sqlite3
from collections.abc import Generator
from model.bodymodel import *
from configuration import *


def write_cache_model(num: int):
    """
    Record model id.
    """
    with open(RTPATH + "cache/periousValue.dll", 'w', encoding='UTF-8') as w:
        w.write(str(num))


def load_cache_model() -> BodyModel:
    """
    Read model id.
    """
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
    Create a model based on id, with original info information.
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
    Generate previous, next, first, first within the bounds system.
    If the value passed in is not in the database,
    jump to the value closest to this value (take the last digit if the distance is the same).
    :param value: model value
    :param direction: next 1; previous -1; jump 0
    :return BodyModel Object
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
        values.sort()  # Sorted from largest to smallest
        maxidx = len(values)
        minidx = 0
        # Dichotomy query the value with the smallest difference
        while maxidx - minidx > 1:
            mididx = (maxidx - minidx) // 2 + minidx
            if values[mididx] > value:
                maxidx = mididx
            else:
                minidx = mididx
        idx = minidx if value - values[minidx] < values[maxidx] - value else maxidx
    return create_by_value(values[idx])


def produce_by_search(kws: str, sysid: int | None) -> Generator[BodyModel]:
    """
    According to keywords and system restrictions, search and generate models without sentence information.
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
    Load all associated sentences based on model vlaue.
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
    """
    Save all relationships of a model base on paragraph attribute of model.
    According to the assertion, it is judged to be blank content, and all sentences are deleted.
    """
    try:
        model.convert_into_sentences()
    except AssertionError:
        model.clean_sentences()
    saving_model(model)


def saving_model(body: BodyModel):
    """
    Save all relationships of a model.
    """
    db, cur = open_database()
    # Read existing relationship
    cur.execute("SELECT text_hash FROM ia_connect WHERE model_value=%d ORDER BY order_id" % body.value)
    hash_exists = [x[0] for x in cur.fetchall()]
    idxes_excluded = set()

    # Loop through each sentence
    for idx_now, sentence in enumerate(body):
        hash_now = sentence.gethash
        # Determine whether the relationship already exists
        if hash_now in hash_exists:
            idx_exists = hash_exists.index(hash_now)
            # Change the sequence number if the sequence changes
            if idx_exists != idx_now:
                cur.execute(
                    "UPDATE ia_connect SET order_id=? WHERE model_value=? AND text_hash=?",
                    (idx_now, body.value, hash_now)
                )
            # Record existing sentences that need to be kept
            idxes_excluded.add(idx_exists)
            continue
        # Judge whether the sentence exists, save the sentence if it does not exist
        cur.execute("SELECT COUNT(*) FROM attribution WHERE text_hash='%s'" % hash_now)
        if cur.fetchone()[0] == 0:
            cur.execute(
                "INSERT INTO attribution (context,text_hash) VALUES (?,?)", (sentence.value, hash_now)
            )
        # Saving relationship
        cur.execute(
            "INSERT INTO ia_connect (model_value,text_hash,order_id) VALUES (?,?,?)",
            (body.value, hash_now, idx_now)
        )

    # Remove irrelevant sentence relations
    cur.executemany(
        "DELETE FROM ia_connect WHERE model_value=? AND text_hash=?",
        ((body.value, hash_) for i, hash_ in enumerate(hash_exists) if i not in idxes_excluded)
    )
    db.commit()
    db.close()


def get_old_info(value: int) -> str:
    """
    Get old version information.
    """
    db, cur = open_database()
    cur.execute("SELECT info FROM info WHERE value=%d" % value)
    context = cur.fetchone()

    assert context is not None
    context = context[0]

    assert context is not None
    context.strip()
    return context


def export_database_json(_path):
    """
    Export database as json file.
    """
    tables = {"attribution", "ia_connect"}
    db, cur = open_database()

    def _export(name):
        cur.execute(f"PRAGMA table_info({name})")
        keys = [x[1] for x in cur.fetchall()]

        cur.execute(f"SELECT {','.join(keys)} FROM {name}")
        data = [{k: v for k, v in zip(keys, row)} for row in cur.fetchall()]

        data_json = json.dumps(data, ensure_ascii=False)
        with open(f"{_path}/{name}.json", 'w', encoding='UTF-8') as f:
            f.write(data_json)

    for key in tables:
        _export(key)
    db.close()
    return tables


def import_database_from_json(_path):
    """
    Import database from json file.
    """
    tables = {"attribution": 0, "ia_connect": 0}
    db, cur = open_database()

    def _insert(name):
        with open(f"{_path}/{name}.json", "r", encoding="UTF-8") as f:
            data = f.read().strip()
        data = json.loads(data)
        count = 0
        for row in data:
            # Query for duplicate items, and exclude fields with empty values when querying
            cur.execute(
                f"SELECT COUNT(*) FROM {name} WHERE {' AND '.join(f'{i}=:{i}' for i in row if row[i] is not None)}",
                row
            )
            if cur.fetchone()[0] == 0:
                cur.execute(f"INSERT INTO {name} ({','.join(row)}) VALUES ({','.join(f':{i}' for i in row)})", row)
                db.commit()
                count += 1
        return count
    for key in tables:
        tables[key] = _insert(key)
    db.close()
    return tables


def percentage_of_progress_completed(gender: int | None, sysid: int) -> int:
    """
    Calculate the percentage complete of a system.
    :param gender: 0 or 1
    :param sysid: if -1, then no system is specified
    :return: Integer part of a percentage
    """
    db, cur = open_database()
    match (gender is None, sysid == -1):
        case (False, True):
            attach = " WHERE sex=%d" % gender
        case (True, False):
            attach = " WHERE sysid=%d" % sysid
        case (False, False):
            attach = " WHERE sex=%d AND sysid=%d" % (gender, sysid)
        case _:
            attach = ""

    cur.execute(f"SELECT value FROM info" + attach)
    values = [str(x[0]) for x in cur.fetchall()]

    cur.execute(f"SELECT COUNT(DISTINCT model_value) FROM ia_connect WHERE model_value IN ({','.join(values)})")
    number = cur.fetchone()[0]

    percentage = int(number / len(values) * 100)
    if percentage > 100:
        percentage = 100
    return percentage
