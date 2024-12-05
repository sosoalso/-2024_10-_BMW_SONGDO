# ---------------------------------------------------------------------------- #
import asyncio

from blucontroller import BluComponentState, BluController, db_to_tp
from buttonhandler import ButtonHandler
from lib_tp import tp_add_watcher, tp_send_level, tp_set_button, tp_set_button_text
from mojo import context

# ---------------------------------------------------------------------------- #
DV_MUSE = context.devices.get("idevice")
# ---------------------------------------------------------------------------- #
DV_RELAY = DV_MUSE.relay
# ---------------------------------------------------------------------------- #
DV_BLU = context.devices.get("SoundwebLondonBLU-100-111")
# ---------------------------------------------------------------------------- #
# DV_TP_10001 = context.devices.get("AMX-10001")
# DV_TP_10002 = context.devices.get("AMX-10002")
# DV_TP_10003 = context.devices.get("AMX-10003")
DV_TP_10004 = context.devices.get("AMX-10004")
DV_TP_10005 = context.devices.get("AMX-10005")
# TP_LIST = [DV_TP_10001, DV_TP_10002, DV_TP_10003, DV_TP_10004]
TP_LIST = [DV_TP_10004, DV_TP_10005]
# ---------------------------------------------------------------------------- #
# INFO : 자료 저장
# ---------------------------------------------------------------------------- #
BLU_COMPONENT_STATES = BluComponentState()
# ---------------------------------------------------------------------------- #
# INFO : 컴포넌트 경로
# ---------------------------------------------------------------------------- #
BLU_PATH_MAIN_MIXER_GAIN = [("Main Mixer", f"Channel {index_ch}", "Gain") for index_ch in range(1, 12 + 1)] + [
    ("Driving Center Source", "Channel 2", "Gain")
]
BLU_PATH_MAIN_MIXER_MUTE = [("Main Mixer", f"Channel {index_ch}", "Mute") for index_ch in range(1, 12 + 1)] + [
    ("Driving Center Source", "Channel 2", "Mute")
]
BLU_PATH_CONTROL_LEVEL_GAIN = [("Control Level", f"Channel {index_ch}", "Gain") for index_ch in range(1, 4 + 1)]
# [("Control Level", "Master")] +
BLU_PATH_CONTROL_LEVEL_MUTE = [("Control Level", f"Channel {index_ch}", "Mute") for index_ch in range(1, 4 + 1)]
# [("Control Level", "Override Mute")] +

BLU_PATH_MAIN_OUT_USER_EQ = [("Main Out User EQ", f"Band {index_ch}", "Boost_Cut") for index_ch in range(1, 3 + 1)]
# ---------------------------------------------------------------------------- #
# INFO : BLU 컨트롤러 초기화
# ---------------------------------------------------------------------------- #
blu_controller = BluController(DV_BLU, BLU_COMPONENT_STATES)


def handle_blu_controller_online(*args):
    blu_controller.init(
        BLU_PATH_MAIN_MIXER_MUTE,
        BLU_PATH_MAIN_MIXER_GAIN,
        BLU_PATH_CONTROL_LEVEL_MUTE,
        BLU_PATH_CONTROL_LEVEL_GAIN,
        BLU_PATH_MAIN_OUT_USER_EQ,
    )


blu_controller.device.online(handle_blu_controller_online)


# ---------------------------------------------------------------------------- #
# INFO : path 에 따라서 터치판넬 피드백 업데이트
# ---------------------------------------------------------------------------- #
def ui_refresh_blu_button_by_path(path):
    try:
        # ---------------------------------------------------------------------------- #
        if path in BLU_PATH_MAIN_MIXER_MUTE:
            idx = BLU_PATH_MAIN_MIXER_MUTE.index(path)
            ch_index = 11 + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_set_button(tp, 4, ch_index, val == "Muted")
        # ---------------------------------------------------------------------------- #
        elif path in BLU_PATH_MAIN_MIXER_GAIN:
            idx = BLU_PATH_MAIN_MIXER_GAIN.index(path)
            lvl_index = 11 + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_send_level(tp, 4, lvl_index, int(round(db_to_tp(float(val)), 0)))
                    tp_set_button_text(tp, 4, lvl_index, f"{round(val, 1)} db")
        # ---------------------------------------------------------------------------- #
        elif path in BLU_PATH_CONTROL_LEVEL_MUTE:
            idx = BLU_PATH_CONTROL_LEVEL_MUTE.index(path)
            ch_index = 71 + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_set_button(tp, 4, ch_index, val == "Muted")
        # ---------------------------------------------------------------------------- #
        elif path in BLU_PATH_CONTROL_LEVEL_GAIN:
            idx = BLU_PATH_CONTROL_LEVEL_GAIN.index(path)
            lvl_index = 71 + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_send_level(tp, 4, lvl_index, int(round(db_to_tp(float(val)), 0)))
                    tp_set_button_text(tp, 4, lvl_index, f"{round(val, 1)} db")

        # ---------------------------------------------------------------------------- #
        elif path in BLU_PATH_MAIN_OUT_USER_EQ:
            idx = BLU_PATH_MAIN_OUT_USER_EQ.index(path)
            lvl_index = 101 + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_send_level(tp, 4, lvl_index, int(round(db_to_tp(float(val)), 0)))
                    tp_set_button_text(tp, 4, lvl_index, f"{round(val, 1)} db")
        # ---------------------------------------------------------------------------- #

    except Exception as e:
        print(e)


# ---------------------------------------------------------------------------- #
# WARN : BLU 컨트롤러의 상태가 변경되면 UI를 업데이트하는 옵저버 구독좋아요댓글알림설정!
# ---------------------------------------------------------------------------- #
blu_controller.component_states.subscribe(ui_refresh_blu_button_by_path)


# ---------------------------------------------------------------------------- #
# INFO : 터치패널 버튼 이벤트 등록
# ---------------------------------------------------------------------------- #
def tp_add_blu_button_event(evt):
    tp = evt.source
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_MAIN_MIXER_MUTE):
        btn_index = 11 + idx
        mute_toggle_btn = ButtonHandler()
        mute_toggle_btn.add_event_handler("push", lambda path=path: blu_controller.toggle_muted_unmuted(path))
        tp_add_watcher(tp, 4, btn_index, mute_toggle_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_MAIN_MIXER_GAIN):
        # print(f"{idx=}, {path=} type={type(path)}")
        btn_vol_up_index = 31 + idx
        btn_vol_down_index = 51 + idx
        vol_up_btn = ButtonHandler(repeat_interval=0.1)
        vol_dn_btn = ButtonHandler(repeat_interval=0.1)
        vol_up_btn.add_event_handler("repeat", lambda path=path: blu_controller.vol_up(path))
        vol_dn_btn.add_event_handler("repeat", lambda path=path: blu_controller.vol_down(path))
        tp_add_watcher(tp, 4, btn_vol_up_index, vol_up_btn.handle_event)
        tp_add_watcher(tp, 4, btn_vol_down_index, vol_dn_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_CONTROL_LEVEL_MUTE):
        # print(f"{idx=}, {path=} type={type(path)}")
        btn_index = 71 + idx
        mute_toggle_btn = ButtonHandler()
        mute_toggle_btn.add_event_handler("push", lambda path=path: blu_controller.toggle_muted_unmuted(path))
        tp_add_watcher(tp, 4, btn_index, mute_toggle_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_CONTROL_LEVEL_GAIN):
        btn_vol_up_index = 81 + idx
        btn_vol_down_index = 91 + idx
        vol_up_btn = ButtonHandler(repeat_interval=0.1)
        vol_dn_btn = ButtonHandler(repeat_interval=0.1)
        vol_up_btn.add_event_handler("repeat", lambda path=path: blu_controller.vol_up(path))
        vol_dn_btn.add_event_handler("repeat", lambda path=path: blu_controller.vol_down(path))
        tp_add_watcher(tp, 4, btn_vol_up_index, vol_up_btn.handle_event)
        tp_add_watcher(tp, 4, btn_vol_down_index, vol_dn_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_MAIN_OUT_USER_EQ):
        btn_vol_up_index = 111 + idx
        btn_vol_down_index = 121 + idx
        vol_up_btn = ButtonHandler(repeat_interval=0.1)
        vol_dn_btn = ButtonHandler(repeat_interval=0.1)
        vol_up_btn.add_event_handler("repeat", lambda path=path: blu_controller.vol_up(path))
        vol_dn_btn.add_event_handler("repeat", lambda path=path: blu_controller.vol_down(path))
        tp_add_watcher(tp, 4, btn_vol_up_index, vol_up_btn.handle_event)
        tp_add_watcher(tp, 4, btn_vol_down_index, vol_dn_btn.handle_event)
        ui_refresh_blu_button_by_path(path)


# ---------------------------------------------------------------------------- #


def handle_tp_event(*args):
    for tp in TP_LIST:
        tp.online(tp_add_blu_button_event)


DV_MUSE.online(handle_tp_event)
# ---------------------------------------------------------------------------- #
context.run(globals())
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
