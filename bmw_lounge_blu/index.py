# ---------------------------------------------------------------------------- #
from blucontroller import BluComponentState, BluController, db_to_tp
from buttonhandler import ButtonHandler
from lib_tp import tp_add_watcher, tp_send_level, tp_set_button, tp_set_button_text
from mojo import context

# ---------------------------------------------------------------------------- #
DV_MUSE = context.devices.get("idevice")
# ---------------------------------------------------------------------------- #
DV_BLU = context.devices.get("SoundwebLondonBLU-100-101")
# ---------------------------------------------------------------------------- #
DV_TP_10001 = context.devices.get("AMX-10001")
DV_TP_10002 = context.devices.get("AMX-10002")
DV_TP_10003 = context.devices.get("AMX-10003")
# ---------------------------------------------------------------------------- #
TP_LIST = [DV_TP_10001, DV_TP_10002, DV_TP_10003]
# ---------------------------------------------------------------------------- #
# INFO : 자료 저장
# ---------------------------------------------------------------------------- #
BLU_COMPONENT_STATES = BluComponentState()
# ---------------------------------------------------------------------------- #
# INFO : 컴포넌트 경로
# ---------------------------------------------------------------------------- #
BLU_PATH_BGM_MATRIX = [
    ("BGM Matrix", f"Output {index_out}", f"Input {index_in} On_Off")
    for index_in in range(1, 4 + 1)
    for index_out in range(1, 10 + 1)
]
BLU_PATH_MIC_AND_CHIME_MATRIX = [
    ("Mic and Chime Matrix", f"Output {index_out}", f"Input {index_in} On_Off")
    for index_in in range(1, 5 + 1)
    for index_out in range(1, 10 + 1)
]
BLU_PATH_CONTROL_LEVEL_GAIN = [("Control Level", f"Channel {index_ch}", "Gain") for index_ch in range(1, 8 + 1)]
BLU_PATH_CONTROL_LEVEL_MUTE = [("Control Level", f"Channel {index_ch}", "Mute") for index_ch in range(1, 8 + 1)]
BLU_PATH_BYPASS_BGM = [
    ("Plaza BGM Ducker", "Bypass"),
    # ("Driving BGM Ducker", "Bypass"),
    # ("Welcome CMS Ducker", "Bypass"),
    # ("Info Desk SoV Ducker", "Bypass"),
]
# ---------------------------------------------------------------------------- #
# INFO : BLU 컨트롤러 초기화
# ---------------------------------------------------------------------------- #
blu_controller = BluController(DV_BLU, BLU_COMPONENT_STATES)


def handle_blu_controller_online(*args):
    blu_controller.init(
        BLU_PATH_BGM_MATRIX,
        BLU_PATH_MIC_AND_CHIME_MATRIX,
        BLU_PATH_CONTROL_LEVEL_GAIN,
        BLU_PATH_CONTROL_LEVEL_MUTE,
        BLU_PATH_BYPASS_BGM,
    )


blu_controller.device.online(handle_blu_controller_online)
# ---------------------------------------------------------------------------- #
# INFO : 버튼 인덱스
# ---------------------------------------------------------------------------- #
BTN_INDEX_CH_BGM_MTX_ST = 101
BTN_INDEX_CH_MIC_MTX_ST = 201
# ---------------------------------------------------------------------------- #
BTN_INDEX_LV_GAIN_ST = 11  # 11 ~ 18
BTN_INDEX_CH_MUTE_ST = 11  # 11 ~ 18
BTN_INDEX_CH_VOL_UP_ST = 31  # 31 ~ 38
BTN_INDEX_CH_VOL_DN_ST = 51  # 51 ~ 58
# ---------------------------------------------------------------------------- #
BTN_INDEX_CH_VOL_UP_ALL = 71
BTN_INDEX_CH_VOL_DN_ALL = 72
BTN_INDEX_CH_VOL_MUTE_ALL = 70
# ---------------------------------------------------------------------------- #
BTN_INDEX_CH_BGM_CLEAR = 80
BTN_INDEX_CH_BGM_I_TO_ALL_ST = 81  # 81 ~ 84
# ---------------------------------------------------------------------------- #
BTN_INDEX_CH_MIC_CLEAR = 90
BTN_INDEX_CH_MIC_I_TO_ALL_ST = 91  # 91 ~ 95
# ---------------------------------------------------------------------------- #
BTN_INDEX_CH_BGM_BYPASS = 1  # 1 ~ 4
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
# INFO : path 에 따라서 터치판넬 피드백 업데이트
# ---------------------------------------------------------------------------- #
def ui_refresh_blu_button_by_path(path):
    try:
        if path in BLU_PATH_BGM_MATRIX:
            idx = BLU_PATH_BGM_MATRIX.index(path)
            ch_index = BTN_INDEX_CH_BGM_MTX_ST + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_set_button(tp, 2, ch_index, val == "On")
        # ---------------------------------------------------------------------------- #
        elif path in BLU_PATH_MIC_AND_CHIME_MATRIX:
            idx = BLU_PATH_MIC_AND_CHIME_MATRIX.index(path)
            ch_index = BTN_INDEX_CH_MIC_MTX_ST + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_set_button(tp, 2, ch_index, val == "On")
        # ---------------------------------------------------------------------------- #
        elif path in BLU_PATH_CONTROL_LEVEL_GAIN:
            idx = BLU_PATH_CONTROL_LEVEL_GAIN.index(path)
            lvl_index = BTN_INDEX_LV_GAIN_ST + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_send_level(tp, 2, lvl_index, int(round(db_to_tp(float(val)), 0)))
                    tp_set_button_text(tp, 2, lvl_index, f"{round(val, 1)} db")
        # ---------------------------------------------------------------------------- #
        elif path in BLU_PATH_CONTROL_LEVEL_MUTE:
            idx = BLU_PATH_CONTROL_LEVEL_MUTE.index(path)
            ch_index = BTN_INDEX_CH_MUTE_ST + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_set_button(tp, 2, ch_index, val == "Muted")
        # ---------------------------------------------------------------------------- #
        elif path in BLU_PATH_BYPASS_BGM:
            idx = BLU_PATH_BYPASS_BGM.index(path)
            ch_index = BTN_INDEX_CH_BGM_BYPASS + idx
            val = blu_controller.component_states.get_state(path)
            if val is not None:
                for tp in TP_LIST:
                    tp_set_button(tp, 2, ch_index, val == "On")
    except Exception as e:
        print(f"ui_refresh_blu_button_by_path exception {path} {e}")


# ---------------------------------------------------------------------------- #
# WARN : BLU 컨트롤러의 상태가 변경되면 UI를 업데이트하는 옵저버 구독좋아요댓글알림설정!
# ---------------------------------------------------------------------------- #
blu_controller.component_states.subscribe(ui_refresh_blu_button_by_path)
# ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #
# INFO : 커스텀 펑션 ㅠ
# ---------------------------------------------------------------------------- #
def blu_clear_bgm():
    for path in BLU_PATH_BGM_MATRIX:
        blu_controller.set_off(path)


def blu_toggle_bgm_to_all(index_bgm):
    if index_bgm < 1 or index_bgm > 4:
        return
    start_idx = (index_bgm - 1) * 10
    end_idx = (index_bgm * 10) - 1  # vision forum 빼고
    filtered_idx_list = [i for i in range(start_idx, end_idx)]
    base_val = blu_controller.component_states.get_state(BLU_PATH_BGM_MATRIX[start_idx])
    for idx in filtered_idx_list:
        if base_val == "On":
            blu_controller.set_off(BLU_PATH_BGM_MATRIX[idx])
        else:
            blu_controller.set_on(BLU_PATH_BGM_MATRIX[idx])


def blu_clear_mic():
    for path in BLU_PATH_MIC_AND_CHIME_MATRIX:
        blu_controller.set_off(path)


def blu_toggle_mic_to_all(index_mic):
    if index_mic < 1 or index_mic > 5:
        return
    start_idx = (index_mic - 1) * 10
    end_idx = index_mic * 10 - 1  # vision forum 빼고
    filtered_idx_list = [i for i in range(start_idx, end_idx)]
    base_val = blu_controller.component_states.get_state(BLU_PATH_MIC_AND_CHIME_MATRIX[start_idx])
    for idx in filtered_idx_list:
        if base_val == "On":
            blu_controller.set_off(BLU_PATH_MIC_AND_CHIME_MATRIX[idx])
        else:
            blu_controller.set_on(BLU_PATH_MIC_AND_CHIME_MATRIX[idx])


def blu_vol_up_all():
    for path in BLU_PATH_CONTROL_LEVEL_GAIN:
        blu_controller.vol_up(path)


def blu_vol_dn_all():
    for path in BLU_PATH_CONTROL_LEVEL_GAIN:
        blu_controller.vol_down(path)


def blu_mute_all():
    base_val = blu_controller.component_states.get_state(BLU_PATH_CONTROL_LEVEL_MUTE[0])
    for path in BLU_PATH_CONTROL_LEVEL_MUTE:
        if base_val == "Muted":
            blu_controller.set_unmuted(path)
        else:
            blu_controller.set_muted(path)


# ---------------------------------------------------------------------------- #
# INFO : 터치패널 버튼 이벤트 등록
# ---------------------------------------------------------------------------- #
def tp_add_blu_button_event(evt):
    tp = evt.source
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_BGM_MATRIX):
        btn_index = BTN_INDEX_CH_BGM_MTX_ST + idx
        mtx_toggle_btn = ButtonHandler()
        mtx_toggle_btn.add_event_handler("push", lambda path=path: blu_controller.toggle_on_off(path))
        tp_add_watcher(tp, 2, btn_index, mtx_toggle_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    for idx in range(0, 4):
        btn_bgm_to_all = ButtonHandler()
        btn_bgm_to_all.add_event_handler("push", lambda index_bgm=idx + 1: blu_toggle_bgm_to_all(index_bgm))
        tp_add_watcher(tp, 2, BTN_INDEX_CH_BGM_I_TO_ALL_ST + idx, btn_bgm_to_all.handle_event)
    # ---------------------------------------------------------------------------- #
    btn_bgm_clear = ButtonHandler()
    btn_bgm_clear.add_event_handler("push", blu_clear_bgm)
    tp_add_watcher(tp, 2, BTN_INDEX_CH_BGM_CLEAR, btn_bgm_clear.handle_event)
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_MIC_AND_CHIME_MATRIX):
        btn_index = BTN_INDEX_CH_MIC_MTX_ST + idx
        mtx_toggle_btn = ButtonHandler()
        mtx_toggle_btn.add_event_handler("push", lambda path=path: blu_controller.toggle_on_off(path))
        tp_add_watcher(tp, 2, btn_index, mtx_toggle_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    for idx in range(0, 5):
        btn_mic_to_all = ButtonHandler()
        btn_mic_to_all.add_event_handler("push", lambda index_mic=idx + 1: blu_toggle_mic_to_all(index_mic))
        tp_add_watcher(tp, 2, BTN_INDEX_CH_MIC_I_TO_ALL_ST + idx, btn_mic_to_all.handle_event)
    # ---------------------------------------------------------------------------- #
    btn_mic_clear = ButtonHandler()
    btn_mic_clear.add_event_handler("push", blu_clear_mic)
    tp_add_watcher(tp, 2, BTN_INDEX_CH_MIC_CLEAR, btn_mic_clear.handle_event)
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_CONTROL_LEVEL_GAIN):
        btn_vol_up_index = BTN_INDEX_CH_VOL_UP_ST + idx
        btn_vol_down_index = BTN_INDEX_CH_VOL_DN_ST + idx
        vol_up_btn = ButtonHandler(repeat_interval=0.2)
        vol_dn_btn = ButtonHandler(repeat_interval=0.2)
        vol_up_btn.add_event_handler("repeat", lambda path=path: blu_controller.vol_up(path))
        vol_dn_btn.add_event_handler("repeat", lambda path=path: blu_controller.vol_down(path))
        tp_add_watcher(tp, 2, btn_vol_up_index, vol_up_btn.handle_event)
        tp_add_watcher(tp, 2, btn_vol_down_index, vol_dn_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_CONTROL_LEVEL_MUTE):
        btn_index = BTN_INDEX_CH_MUTE_ST + idx
        mute_toggle_btn = ButtonHandler()
        mute_toggle_btn.add_event_handler("push", lambda path=path: blu_controller.toggle_muted_unmuted(path))
        tp_add_watcher(tp, 2, btn_index, mute_toggle_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    for idx, path in enumerate(BLU_PATH_BYPASS_BGM):
        btn_index = BTN_INDEX_CH_BGM_BYPASS + idx
        bypass_toggle_btn = ButtonHandler()
        bypass_toggle_btn.add_event_handler("push", lambda path=path: blu_controller.toggle_on_off(path))
        tp_add_watcher(tp, 2, btn_index, bypass_toggle_btn.handle_event)
        ui_refresh_blu_button_by_path(path)
    # ---------------------------------------------------------------------------- #
    btn_vol_up_all = ButtonHandler(repeat_interval=0.4)
    btn_vol_up_all.add_event_handler("repeat", blu_vol_up_all)
    tp_add_watcher(tp, 2, BTN_INDEX_CH_VOL_UP_ALL, btn_vol_up_all.handle_event)
    btn_vol_dn_all = ButtonHandler(repeat_interval=0.4)
    btn_vol_dn_all.add_event_handler("repeat", blu_vol_dn_all)
    tp_add_watcher(tp, 2, BTN_INDEX_CH_VOL_DN_ALL, btn_vol_dn_all.handle_event)
    btn_mute_all = ButtonHandler()
    btn_mute_all.add_event_handler("push", blu_mute_all)
    tp_add_watcher(tp, 2, BTN_INDEX_CH_VOL_MUTE_ALL, btn_mute_all.handle_event)
    # ---------------------------------------------------------------------------- #


# ---------------------------------------------------------------------------- #


def handle_tp_event(*arg):
    for tp in TP_LIST:
        tp.online(tp_add_blu_button_event)


DV_MUSE.online(handle_tp_event)
# ---------------------------------------------------------------------------- #
context.run(globals())
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
# ---------------------------------------------------------------------------- #
