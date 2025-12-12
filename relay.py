import time
import hid

class Relay(object):
	"""docstring for Relay"""
	def __init__(self, idVendor=0x16c0, idProduct=0x05df):
		self.h = hid.device()
		self.h.open(idVendor, idProduct)
		self.h.set_nonblocking(1)

	def get_switch_statuses_from_report(self, report):
		switch_statuses = report[7] # Grab the 8th number, which is a integer
		switch_statuses = [int(x) for x in list('{0:08b}'.format(switch_statuses))] # Convert the integer to a binary, and the binary to a list.
		switch_statuses.reverse() # Reverse the list, since the status reads from right to left

		# The switch_statuses now looks something like this:
		# [1, 1, 0, 0, 0, 0, 0, 0]
		# Switch 1 and 2 (index 0 and 1 respectively) are on, the rest are off.

		return switch_statuses

	def send_feature_report(self, message):
		self.h.send_feature_report(message)

	def get_feature_report(self):
		# If 0 is passed as the feature, then 0 is prepended to the report. However,
		# if 1 is passed, the number is not added and only 8 chars are returned.
		feature = 1
		# This is the length of the report. 
		length = 8
		return self.h.get_feature_report(feature, length)

	def state(self, relay, on=None):
		# Getter
		if on == None:
			if relay == 0:
				report = self.get_feature_report()
				switch_statuses = self.get_switch_statuses_from_report(report)
				status = []
				for s in switch_statuses:
					status.append(bool(s))
			else:
				report = self.get_feature_report()
				switch_statuses = self.get_switch_statuses_from_report(report)
				status = bool(switch_statuses[relay-1])

			return status

		# Setter
		else:
			if relay == 0:
				if on:
					message = [0xFE]
				else:
					message = [0xFC]
			else:
				if on:
					message = [0xFF, relay]
				else:
					message = [0xFD, relay]

			self.send_feature_report(message)


class RelayController:
    def __init__(self, relay_cmd_queue, tray_size=1000, tick=0.01):
        self.relay_cmd_queue = relay_cmd_queue
        self.tray_size = tray_size
        self.tick = tick

        # Tray 초기화
        self.tray = [[] for _ in range(tray_size)]
        self.current_index = 0

        # 외부 프로세스에서 종료시키도록 flag 사용
        self.running = True

    def stop(self):
        self.running = False

    # 동일 tick 내 여러 명령을 병합
    def merge_commands(self, slot):
        merged = {}
        for state, port in slot:
            merged[port] = state
        return merged

    # Relay 명령 실행
    def execute(self, commands, relay):
        for port, state in commands.items():
            if state == "ON":
                relay.state(port, on=True)
            else:
                relay.state(port, on=False)

    # 프로세스 내에서 실행될 함수
    def run(self):
        relay = Relay()  # 반드시 프로세스 안에서 생성해야 HID 충돌 X

        while self.running:
            # ───────────────────────────────
            # 1. Queue 수신 (Non-blocking)
            # ───────────────────────────────
            try:
                while True:
                    signal_type, relay_port, delay, duration = self.relay_cmd_queue.get_nowait()
                    
                    # === 종료 신호 ===
                    if signal_type == "EXIT": 
                        try: # 모든 릴레이 OFF
                            relay.state(0, on=False)
                            print("[RelayController] All relays turned OFF.")
                        except Exception as e:
                            print("[RelayController] Error turning off relays:", e)

                        # print("[RelayController] Shutting down process...")
                        return  # ← 프로세스 종료

                    start_idx = (self.current_index + int(delay / self.tick)) % self.tray_size
                    end_idx = (start_idx + int(duration / self.tick)) % self.tray_size

                    self.tray[start_idx].append(("ON", relay_port))
                    self.tray[end_idx].append(("OFF", relay_port))

            except Exception:
                pass

            # ───────────────────────────────
            # 2. 현재 slot 처리
            # ───────────────────────────────
            slot = self.tray[self.current_index]
            if slot:
                merged = self.merge_commands(slot)
                self.execute(merged, relay)
                self.tray[self.current_index] = []

            # ───────────────────────────────
            # 3. 다음 tick으로 이동
            # ───────────────────────────────
            self.current_index = (self.current_index + 1) % self.tray_size
            time.sleep(self.tick)

