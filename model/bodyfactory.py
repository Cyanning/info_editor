import json
import sqlite3
from collections.abc import Generator
from model.bodymodel import BodyModel, Sentence
from configuration import (
    VALUE_PATH, DATABASE_PATH
)


def write_cache_model(num: int):
    """
    Record model id.
    """
    with open(VALUE_PATH, 'w', encoding='UTF-8') as w:
        w.write(str(num))


def load_cache_model():
    """
    Read model id.
    """
    try:
        with open(VALUE_PATH, 'r', encoding='UTF-8') as f:
            strings = f.read().strip()
            value = int(strings)
    except FileNotFoundError:
        value = None
    return value


class BodyFactory:
    def __init__(self):
        self.db = sqlite3.connect(DATABASE_PATH)

    def close(self):
        self.db.close()

    def create_by_value(self, value: int):
        """
        Create a model based on id, with original info information.
        """
        # Seek model name
        cur = self.db.cursor()
        cur.execute("SELECT name FROM info WHERE value=%d" % value)
        res = cur.fetchone()
        assert res is not None
        # Seek all sentence's hash
        name = res[0]
        cur.execute("SELECT text_hash FROM ia_connect WHERE model_value=%d ORDER BY order_id" % value)
        sentence_hashes = [x[0] for x in cur.fetchall()]
        # Seek sentence text
        sentences = []
        for sentence_hash in sentence_hashes:
            cur.execute("SELECT context FROM attribution WHERE text_hash='%s'" % sentence_hash)
            try:
                sentences.append(cur.fetchone()[0])
            except (TypeError, IndexError):
                continue
        # Objective model
        return BodyModel(value, name, sentences)

    def setup_model(self, value: int, direction: int = 0):
        """
        Generate previous, next, first, first within the bounds system.
        If the value passed in is not in the database,
        jump to the value closest to this value (take the last digit if the distance is the same).
        :param value: model value
        :param direction: next 1; previous -1; jump 0
        :return BodyModel Object
        """
        assert 100000 <= value < 212000 or 1000000 <= value < 2120000

        if direction == 1 or direction == -1:
            cur = self.db.cursor()
            cur.execute(f"SELECT value FROM info ORDER BY sysid,value")
            values = [x[0] for x in cur.fetchall()]
            if value in values:
                idx = values.index(value) + direction
                idx %= len(values)  # Make sure the index is in range
                final_val = values[idx]
            else:
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
                if value - values[minidx] < values[maxidx] - value:
                    final_val = values[minidx]
                else:
                    final_val = values[maxidx]
        elif direction == 0:
            final_val = value
        else:
            raise ValueError

        return self.create_by_value(final_val)

    def produce_by_search(self, kws: str, sysid: int | None) -> Generator[BodyModel]:
        """
        According to keywords and system restrictions, search and generate models without sentence information.
        """
        cur = self.db.cursor()
        sql = "SELECT value,name FROM info WHERE name LIKE '%{}%' OR info LIKE '%{}%' OR value LIKE '%{}%'".format(
            kws, kws, kws
        )
        if sysid is not None:
            sql += f" AND sysid={sysid}"
        cur.execute(sql)
        for val, name in cur.fetchall():
            yield BodyModel(val, name)

    def produce_sentences_by_value(self, value: int) -> list[Sentence]:
        """
        Load all associated sentences based on model vlaue.
        """
        cur = self.db.cursor()
        cur.execute(f"SELECT text_hash FROM ia_connect WHERE model_value={value} ORDER BY order_id")
        for thash in (x[0] for x in cur.fetchall()):
            cur.execute("SELECT context FROM attribution WHERE text_hash='%s'" % thash)
            try:
                yield Sentence(cur.fetchone()[0])
            except TypeError:
                continue

    def saving_model(self, body: BodyModel):
        """
        Save all relationships of a model.
        """
        cur = self.db.cursor()
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
        self.db.commit()

    def get_old_info(self, value: int) -> str:
        """
        Get old version information.
        """
        cur = self.db.cursor()
        cur.execute("SELECT info FROM info WHERE value=%d" % value)
        context = cur.fetchone()
        try:
            context = context[0]
            context.strip()
        except (TypeError, AttributeError):
            context = ""
        return context

    def export_database_json(self, _path):
        """
        Export database as json file.
        """
        tables = {"attribution", "ia_connect"}
        cur = self.db.cursor()

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
        return tables

    def export_undone_model(self, _path, sysid: int | None, gender: int | None):
        """
        Export the models id which hadn't new content.
        """
        condition = ""
        if sysid is not None:
            condition += f" AND sysid={sysid}"
        if gender is not None:
            condition += f" AND sex={gender}"

        cur = self.db.cursor()
        cur.execute(
            "SELECT info.value FROM info LEFT OUTER JOIN ia_connect ON info.value = ia_connect.model_value "
            "WHERE ia_connect.model_value IS NULL" + condition
        )
        values = (str(row[0]) for row in cur.fetchall())
        with open(_path + "未完成id.txt", 'w', encoding='UTF-8') as f:
            f.write("\n".join(values))

    def import_database_from_json(self, _path) -> dict:
        """
        Import database from json file.
        Returns a dictionary consisting of imported data volumes.
        e.q:{table_name: number}
        """
        tables_count = {"attribution": 0, "ia_connect": 0}
        table_unique_fields = {"attribution": ["text_hash", "context"], "ia_connect": ["model_value", "text_hash"]}

        def _insert(name):
            with open(f"{_path}/{name}.json", "r", encoding="UTF-8") as f:
                data = f.read().strip()
                data = json.loads(data)
            count = 0
            for row in data:
                # Query for duplicate items, and exclude fields with empty values when querying.
                cur.execute(
                    "SELECT COUNT(*) FROM {} WHERE {}".format(
                        name, ' AND '.join(f'{field}=:{field}' for field in table_unique_fields[name])
                    ),
                    row
                )
                if cur.fetchone()[0] > 0:
                    continue
                cur.execute(
                    f"INSERT INTO {name} ({','.join(row)}) VALUES ({','.join(f':{field}' for field in row)})",
                    row
                )
                self.db.commit()
                count += 1
            return count

        cur = self.db.cursor()
        for key in tables_count:
            tables_count[key] = _insert(key)
        return tables_count

    def percentage_of_progress_completed(self, sysid: int | None, gender: int | None) -> int:
        """
        Calculate the percentage complete of a system.
        :return: Integer part of a percentage
        """
        condition = ""
        if sysid is not None:
            condition += f" WHERE sysid={sysid}"
        if gender is not None:
            condition += " AND " if condition else " WHERE "
            condition += f"sex={gender}"

        cur = self.db.cursor()
        cur.execute(f"SELECT value FROM info" + condition)
        values = [str(x[0]) for x in cur.fetchall()]

        cur.execute(f"SELECT COUNT(DISTINCT model_value) FROM ia_connect WHERE model_value IN ({','.join(values)})")
        number = cur.fetchone()[0]

        percentage = int(number / len(values) * 100)
        if percentage > 100:
            percentage = 100
        return percentage
