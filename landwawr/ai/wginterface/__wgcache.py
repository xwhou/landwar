# coding:utf-8

import os
import sys
import time
import pickle
import numpy as np
import logging
import math
from itertools import islice


class CacheDecorator(object):
    def __init__(
        self,
        cache_file="cache.pkl",
        save_every_nmiss=100,
        cal_key_fn=None,
        frozen=False,
        log_level="info",
        log_prefix="",
        log_every_ncall=100,
        max_records=100000,
        check_mode=False,
    ):
        # self.func = func
        self.cache_file = cache_file
        cache_dir = os.path.dirname(self.cache_file)
        if cache_dir:
            if not os.path.exists(cache_dir):
                os.makedirs(cache_dir)
        self.memo = {}
        self.memo_new = {}
        self.cache_file_wrapper = CacheFileWrapper(self.cache_file)
        self.count_func = 0
        self.count_cache = 0
        self.time_func = 0
        self.time_cache = 0
        self.hit_rate = 0.0
        self.save_every_nmiss = save_every_nmiss
        self.frozen = frozen
        self.max_records = max_records
        self.num_record = len(self.memo)
        self.check_mode = check_mode

        self.log_prefix = log_prefix
        self.log_every_ncall = log_every_ncall
        if log_level == "warning":
            logging.basicConfig(level=logging.WARNING)
        elif log_level == "error":
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(level=logging.WARNING)

        if os.path.exists(self.cache_file):
            logging.warning("address {}".format(self))
            # logging.warning(
            #     "{} loading from: {}".format(self.log_prefix, self.cache_file)
            # )
            self.load_cache()
            self.num_record = len(self.memo)
            logging.warning(
                "{} loaded from {}: total {} records".format(
                    self.log_prefix, self.cache_file, self.num_record
                )
            )

            # self.cache_file_wrapper.dump(self.memo)
            # self.memo2 = self.cache_file_wrapper.load()
            # assert len(self.memo2) == len(self.memo), "length not equal %d vs %d" % (
            #     len(self.memo2),
            #     len(self.memo),
            # )
            # for key in self.memo:
            #     assert (self.memo[key] - self.memo2[key]).sum() == 0, (
            #         "%s not equal" % key
            #     )

        if cal_key_fn is not None:
            logging.warning(
                "{}using costumed cal_key_fn function: {}".format(
                    self.log_prefix, cal_key_fn
                )
            )
            self.cal_keys = cal_key_fn
        else:
            self.cal_keys = default_cal_keys

        logging.warning("{} CACHE is frozen?: {}".format(self.log_prefix, self.frozen))

    def __call__(self, func):
        # print("calling ...")
        def wrapper(*args, **kwargs):
            slf = args[0]
            # print(type(slf))
            t = time.time()
            # assert func.__name__ == "get_staticobserve_blindmap_p2p"
            update = False
            key = self.cal_keys(*args, **kwargs)
            # print(key)
            if key in self.memo.keys():
                value = self.memo[key]
                if self.check_mode:
                    value_fuc = func(*args, **kwargs)
                    # update = True
                    assert type(value_fuc) == type(value), "CACHE vaule type not equal"
                    if isinstance(value, np.ndarray):
                        assert (
                            value - value_fuc
                        ).sum() == 0, "CACHE vaule value not equal"
                self.time_cache += time.time() - t
                self.count_cache += 1
            else:
                value = func(*args, **kwargs)
                self.time_func += time.time() - t
                self.count_func += 1
                update = True

            if update and not self.frozen and self.num_record < self.max_records:
                self.update_cache(value, *args, **kwargs)
                self.num_record += 1

            count_tot = self.count_cache + self.count_func
            self.hit_rate = self.count_cache / count_tot
            if count_tot % self.log_every_ncall == 0:
                saved_time = (
                    self.time_func / (self.count_func + 0.00001)
                ) * self.count_cache - self.time_cache
                logging.warning(
                    "{} hit rate: {}, {}/{}; cache size: {}; time saved: {}s".format(
                        self.log_prefix,
                        self.hit_rate,
                        self.count_cache,
                        count_tot,
                        self.num_record,
                        saved_time,
                    )
                )

            if update and not self.frozen:
                if (
                    self.count_func % self.save_every_nmiss == 0
                    and self.num_record < self.max_records
                ):
                    self.save_cache()
            return value

        wrapper.__doc__ = func.__doc__
        return wrapper

    def update_cache(self, value, *args, **kwargs):
        key = self.cal_keys(*args, **kwargs)
        self.memo[key] = value
        self.memo_new[key] = value

    def load_cache(self,):
        try:
            with open(self.cache_file, "rb") as f:
                # self.memo = pickle.load(f)
                self.memo = self.cache_file_wrapper.load()
        except Exception as e:
            logging.error(
                "{} loading {} error".format(self.log_prefix, self.cache_file)
            )
            raise (e)

    def save_cache(self,):
        if not self.memo_new:
            return
        logging.warning(
            "{} saving cache to {}, appending {} records".format(
                self.log_prefix, self.cache_file, len(self.memo_new)
            )
        )
        t = time.time()
        if False:
            # multi-processing: using others' memo
            with open(self.cache_file, "rb") as f:
                # pre_memo = pickle.load(f)
                pre_memo = self.cache_file_wrapper.load()
                self.memo.update(pre_memo)
        # with open(self.cache_file, "wb") as f:
        # pickle.dump(self.memo, f)
        self.cache_file_wrapper.dump(self.memo_new)
        self.memo_new = {}
        logging.warning("{} writing time {}".format(self.log_prefix, time.time() - t))

    def log(self):
        saved_time = (
            self.time_func / (self.count_func + 0.000001)
        ) * self.count_cache - self.time_cache
        logging.warning(
            "{} cache file: {}; cache size: {}; total saved time: {}s".format(
                self.log_prefix, self.cache_file, len(self.memo), saved_time
            )
        )


def default_cal_keys(*args, **kwargs):
    return args.__hash__()


def cal_key_for_blindmap_p2p(slf, obop, ubop):
    # "{}{}{}{}".format(
    #         obop.ObjPos, getBopTypeName(bopb)[0], bopb.ObjPos, bopb.ObjHide
    #     )
    key = "{}{}{}{}".format(obop.ObjPos, ubop.A1, ubop.ObjType, ubop.ObjPos)
    return key


class CacheFileWrapper(object):
    def __init__(self, file_path, chunk_size=5000):
        self.file_path = file_path
        self.chunk_size = chunk_size

    def load(self):
        data = {}
        chunk_num = 0

        with open(self.file_path, "rb") as f:
            while True:
                try:
                    d = pickle.load(f)
                    chunk_num += 1
                    data.update(d)
                except EOFError:
                    break
        if chunk_num == 1 and len(data) > self.chunk_size:
            self.dump(data, append=False)

        return data

    def dump(self, data, append=True):
        chunks = math.ceil(len(data) / self.chunk_size)
        if chunks <= 0:
            return
        # print(
        #     "%d data is sliced into %d, each of size %d"
        #     % (len(data), chunks, self.chunk_size)
        # )
        write_model = "ab" if append == True else "wb"
        with open(self.file_path, write_model) as f:
            for d in self._chunks(data, chunks):
                pickle.dump(d, f)
        return

    def _chunks(self, data, size):
        it = iter(data)
        for i in range(0, len(data), size):
            yield {k: data[k] for k in islice(it, size)}

