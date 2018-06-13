import time

from utils.card_interactor import CardInteractor, CardCrashedException
from queue import Queue, Empty
from objects import FuzzerObject, FuzzerInstruction
from config import EXPERT_RULES

from utils.logging import info, warning

#
# FuzzerObject(cla=cla, bitmask=[0, 1, 1, 1, 0])
#
from utils.util import raise_critical_error


class PrefixFuzzer:
    def __init__(self, card_reader, file_writer, ins_start, ins_end, trust_mode, queue=None):
        self.ins_start = ins_start
        self.ins_end = ins_end
        self.trust_mode = trust_mode
        self.file_writer = file_writer
        self.card_interactor = CardInteractor(card_reader)
        self.queue = queue
        self.progress = 0
        self.progress_history = [(time.time(), 0)]

    def run(self):
        info("fuzzer", "Brute forcing every command for each class...")
        self._process_queue()
        info("fuzzer", "Done.")

    def get_classes(self):
        return self._enummerate_classes()

    def add_testcase(self, fuzzer_instruction):
        info("fuzzer", "Adding Fuzz Object {}".format(str(fuzzer_instruction)))
        self.queue.put(fuzzer_instruction)

    def _process_queue(self):
        while True:
            try:
                elem = self.queue.get(block=False)
            except Empty:
                break

            self._fuzz_element(elem)

    def _fuzz_element(self, item):
        if type(item) == FuzzerInstruction:
            for cla in item.get_test_elements(0):
                for ins in item.get_test_elements(1):
                    for p1 in item.get_test_elements(2):
                        for p2 in item.get_test_elements(3):
                            for num in item.get_test_elements(4):
                                fuzz_obj = FuzzerObject(cla, ins, p1, p2, num, [0]*num)
                                res = self.card_interactor.send_element(fuzz_obj)
                                self._process_result(item, res)
        elif type(item) == FuzzerObject:
            res = self.card_interactor.send_element(item)
            self._process_result(item, res)

    def _enummerate_classes(self):
        valid_cla = []

        info("fuzzer", "Enumerating valid classes...")
        for cla in range(0xFF + 1):
            apdu_to_send = [cla, 0x00, 0x00, 0x00]
            try:
                (sw1, sw2, data, timing) = self.card_interactor.send_apdu(apdu_to_send)
            except CardCrashedException as e:
                raise_critical_error("card.interactor", e)
            # unsupported class is 0x6E00
            if (sw1 == 0x6E) and (sw2 == 0x00):
                continue
            else:
                valid_cla.append(cla)

        info("fuzzer", "Found %d valid command classes: " % len(valid_cla))
        if len(valid_cla) == 256:
            warning("fuzzer", "Class Checking seems to be disabled")
            valid_cla = [0x0B]
        else:
            for cla in valid_cla:
                print("%s" % hex(cla))
        return valid_cla

    def _process_result(self, fuzz_inst, fuzz_obj):
        self.progress += 1
        if self.progress % 100 == 0:
            self._print_stats()
        self.file_writer.export_elem_as_json(fuzz_obj)
        if fuzz_inst.follow_expert_rules and self.trust_mode:
            rules = self._get_expert_rule(fuzz_obj)
            for rule in rules:
                self.add_testcase(rule)

    def _get_expert_rule(self, fuzz_obj):
        ret = []
        if fuzz_obj.get_status_code() in EXPERT_RULES:
            mask = EXPERT_RULES[fuzz_obj.get_status_code()]
            template = fuzz_obj.get_inp_data()
            ret.append(FuzzerInstruction(header=template[0:5], data=template[5:], mask=mask, follow_expert_rules=False))
        return ret

    def _print_stats(self):
        act_time = time.time()
        act_progress = self.progress
        self.progress_history.append((act_time, act_progress))

        if len(self.progress_history) > 10:
            (last_time, last_progress) = self.progress_history[-10]
            average = (act_progress-last_progress) / (act_time - last_time)
        else:
            average ="NaN"

        info("fuzzer", "Totaly processed {} in {} seconds. Average Speed for last 1000 Entries: {}".format(self.progress, act_time - self.progress_history[0][0], average))

        pass
