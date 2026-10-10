// Generated static catalog of all 115 RGG property tables in Yakuza 0
#[derive(Clone, Copy, Debug)]
pub struct StaticCol {
    pub name: &'static str,
    pub col_type: u32,
}

#[derive(Clone, Copy, Debug)]
pub struct StaticTable {
    pub par_name: &'static str,
    pub file_name: &'static str,
    pub num_cols: usize,
    pub num_rows: usize,
    pub cols: &'static [StaticCol],
}

static COLS_0: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 2 },
    StaticCol { name: "CLUB", col_type: 2 },
    StaticCol { name: "BIRTHDAY", col_type: 2 },
    StaticCol { name: "HEIGHT", col_type: 2 },
    StaticCol { name: "BLOOD_TYPE", col_type: 2 },
    StaticCol { name: "CONSTELLATION", col_type: 2 },
    StaticCol { name: "FAVORITE", col_type: 2 },
    StaticCol { name: "HATE", col_type: 2 },
    StaticCol { name: "PICT_NAME", col_type: 2 },
    StaticCol { name: "PICT_NAME2", col_type: 2 },
    StaticCol { name: "ROMAN_NAME", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
    StaticCol { name: "CONTENTS_EXP", col_type: 1 },
];

static COLS_1: &[StaticCol] = &[
    StaticCol { name: "CATEGORY", col_type: 2 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "EXPLANATION", col_type: 1 },
];

static COLS_2: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 2 },
    StaticCol { name: "EXP", col_type: 1 },
    StaticCol { name: "STRING", col_type: 1 },
];

static COLS_3: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
];

static COLS_4: &[StaticCol] = &[
    StaticCol { name: "CATEGORY", col_type: 2 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
];

static COLS_5: &[StaticCol] = &[
    StaticCol { name: "CONTENTS", col_type: 1 },
    StaticCol { name: "CONTENTS_EXP", col_type: 1 },
    StaticCol { name: "MSG_WINDOW", col_type: 1 },
    StaticCol { name: "MAIN_EXP", col_type: 1 },
    StaticCol { name: "MAIN_EXP2", col_type: 2 },
    StaticCol { name: "MAIN_EXP3", col_type: 1 },
    StaticCol { name: "MAIN_EXP4", col_type: 2 },
    StaticCol { name: "MAIN_EXP5", col_type: 1 },
    StaticCol { name: "MAIN_EXP6", col_type: 2 },
    StaticCol { name: "MAIN_EXP7", col_type: 2 },
    StaticCol { name: "MAIN_EXP8", col_type: 2 },
    StaticCol { name: "MAIN_EXP9", col_type: 2 },
];

static COLS_6: &[StaticCol] = &[
    StaticCol { name: "TYPE", col_type: 0 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "DEFFICULTY", col_type: 10 },
    StaticCol { name: "PRIZE_FIRST", col_type: 10 },
    StaticCol { name: "PRIZE_SECOND", col_type: 10 },
    StaticCol { name: "PRIZE_THIRD", col_type: 10 },
    StaticCol { name: "PERFECT", col_type: 10 },
    StaticCol { name: "HACT", col_type: 10 },
    StaticCol { name: "QUEST", col_type: 10 },
    StaticCol { name: "TIME_01", col_type: 10 },
    StaticCol { name: "TIME_02", col_type: 10 },
    StaticCol { name: "TIME_03", col_type: 10 },
    StaticCol { name: "TIME_04", col_type: 10 },
    StaticCol { name: "TIME_05", col_type: 10 },
    StaticCol { name: "TIME_06", col_type: 10 },
    StaticCol { name: "TIME_07", col_type: 10 },
    StaticCol { name: "TIME_08", col_type: 10 },
    StaticCol { name: "TIME_09", col_type: 10 },
    StaticCol { name: "TIME_10", col_type: 10 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
    StaticCol { name: "caption_tex", col_type: 0 },
    StaticCol { name: "style_tex", col_type: 0 },
    StaticCol { name: "symbol_tex", col_type: 0 },
    StaticCol { name: "prize_k", col_type: 11 },
    StaticCol { name: "prize_num_k", col_type: 10 },
    StaticCol { name: "prize_m", col_type: 11 },
    StaticCol { name: "prize_num_m", col_type: 10 },
    StaticCol { name: "CAPTION_NAME", col_type: 0 },
];

static COLS_7: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 10 },
    StaticCol { name: "ITEM_ID", col_type: 11 },
    StaticCol { name: "QUANTITY", col_type: 10 },
    StaticCol { name: "KIND", col_type: 10 },
    StaticCol { name: "IS_RANDOM", col_type: 10 },
];

static COLS_8: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 10 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "ANOTHER_NAME", col_type: 0 },
    StaticCol { name: "DESCRIPTION", col_type: 0 },
    StaticCol { name: "NATIONALITY", col_type: 1 },
    StaticCol { name: "CRIME", col_type: 1 },
    StaticCol { name: "WEIGHT", col_type: 10 },
    StaticCol { name: "STYLE", col_type: 1 },
    StaticCol { name: "AGE", col_type: 0 },
    StaticCol { name: "PATH_TEX_VS", col_type: 0 },
    StaticCol { name: "WEAPON_USE", col_type: 2 },
    StaticCol { name: "MANNEQUIN_MOTION_START", col_type: 0 },
    StaticCol { name: "MANNEQUIN_MOTION_POSE", col_type: 1 },
    StaticCol { name: "MANNEQUIN_MOTION_ACTION_A", col_type: 1 },
    StaticCol { name: "MANNEQUIN_MOTION_ACTION_B", col_type: 0 },
    StaticCol { name: "NAME_SHORT", col_type: 0 },
    StaticCol { name: "visible_condition", col_type: 7 },
    StaticCol { name: "ENMA_NO_CHAKAI", col_type: 2 },
    StaticCol { name: "ENMA_NO_TOUEN", col_type: 2 },
    StaticCol { name: "ENMA_NO_KYOUEN", col_type: 2 },
    StaticCol { name: "ENMA_NO_DAIKYOUEN", col_type: 2 },
    StaticCol { name: "RASETSU_NO_CHAKAI", col_type: 2 },
    StaticCol { name: "RASETSU_NO_KYOUEN", col_type: 2 },
    StaticCol { name: "YASHA_YUUGI", col_type: 1 },
    StaticCol { name: "SYARI_YUUGI", col_type: 0 },
    StaticCol { name: "KEIJO_YUUGI", col_type: 1 },
    StaticCol { name: "SYAKUNETSU_YUUGI", col_type: 1 },
    StaticCol { name: "NARAKU_YUUGI", col_type: 1 },
    StaticCol { name: "ZEKKYOU_YUUGI", col_type: 2 },
];

static COLS_9: &[StaticCol] = &[
    StaticCol { name: "TYPE", col_type: 0 },
    StaticCol { name: "STR", col_type: 0 },
];

static COLS_10: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 10 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "ANOTHER_NAME", col_type: 0 },
    StaticCol { name: "ASSIGN_A_ID", col_type: 10 },
    StaticCol { name: "ASSIGN_B_ID", col_type: 10 },
    StaticCol { name: "REMOVE_TEAM_ID", col_type: 10 },
];

static COLS_11: &[StaticCol] = &[
    StaticCol { name: "ACTIVITY_ENUM", col_type: 0 },
    StaticCol { name: "OPEN_STATE", col_type: 9 },
    StaticCol { name: "CATEGORY", col_type: 1 },
    StaticCol { name: "ACTIVITY_NAME", col_type: 1 },
    StaticCol { name: "USE_COUNTER", col_type: 15 },
    StaticCol { name: "SHOP_ID", col_type: 2 },
    StaticCol { name: "PARAM_TYPE", col_type: 10 },
    StaticCol { name: "ENTITY_UID", col_type: 16 },
    StaticCol { name: "ACHIEVEMENT_NUM", col_type: 10 },
    StaticCol { name: "UI_DRAW_UNIT", col_type: 10 },
    StaticCol { name: "SUCCES_SCENARIO_STATE", col_type: 9 },
    StaticCol { name: "ACTIVITY_DETAIL", col_type: 1 },
    StaticCol { name: "ENABLE_KIRYU", col_type: 10 },
    StaticCol { name: "ENABLE_MAJIMA", col_type: 10 },
    StaticCol { name: "format", col_type: 10 },
];

static COLS_12: &[StaticCol] = &[
    StaticCol { name: "DIFFICULTY", col_type: 1 },
    StaticCol { name: "QUESTION", col_type: 0 },
    StaticCol { name: "ANSWER", col_type: 1 },
    StaticCol { name: "LIMIT_TIME", col_type: 1 },
    StaticCol { name: "LT", col_type: 1 },
    StaticCol { name: "CT", col_type: 1 },
    StaticCol { name: "RT", col_type: 1 },
    StaticCol { name: "LC", col_type: 1 },
    StaticCol { name: "CC", col_type: 1 },
    StaticCol { name: "RC", col_type: 1 },
    StaticCol { name: "LB", col_type: 1 },
    StaticCol { name: "CB", col_type: 1 },
    StaticCol { name: "RB", col_type: 1 },
];

static COLS_13: &[StaticCol] = &[
    StaticCol { name: "NUMBER", col_type: 1 },
    StaticCol { name: "1st_x", col_type: 1 },
    StaticCol { name: "1st_y", col_type: 1 },
    StaticCol { name: "1st_z", col_type: 1 },
    StaticCol { name: "1st_layer", col_type: 1 },
    StaticCol { name: "1st_hit", col_type: 1 },
];

static COLS_14: &[StaticCol] = &[
    StaticCol { name: "DIFFICULTY", col_type: 1 },
    StaticCol { name: "FIRST_PIC", col_type: 1 },
    StaticCol { name: "SUCCESS", col_type: 1 },
    StaticCol { name: "FAILURE", col_type: 1 },
    StaticCol { name: "SUCCESS_1", col_type: 1 },
    StaticCol { name: "SUCCESS_2", col_type: 1 },
    StaticCol { name: "SUCCESS_3", col_type: 1 },
    StaticCol { name: "SUCCESS_4", col_type: 1 },
    StaticCol { name: "SUCCESS_5", col_type: 1 },
    StaticCol { name: "ITEM_ID_1", col_type: 11 },
    StaticCol { name: "ITEM_ID_2", col_type: 11 },
    StaticCol { name: "ITEM_ID_3", col_type: 11 },
    StaticCol { name: "ITEM_ID_4", col_type: 11 },
    StaticCol { name: "ITEM_ID_5", col_type: 11 },
];

static COLS_15: &[StaticCol] = &[
    StaticCol { name: "PICTURE", col_type: 0 },
    StaticCol { name: "AT0X", col_type: 1 },
    StaticCol { name: "AT0Y", col_type: 1 },
    StaticCol { name: "AT0R", col_type: 1 },
    StaticCol { name: "AT1X", col_type: 1 },
    StaticCol { name: "AT1Y", col_type: 1 },
    StaticCol { name: "AT1R", col_type: 1 },
    StaticCol { name: "AT2X", col_type: 2 },
    StaticCol { name: "AT2Y", col_type: 2 },
    StaticCol { name: "AT2R", col_type: 2 },
];

static COLS_16: &[StaticCol] = &[
    StaticCol { name: "DIFFICULTY", col_type: 1 },
    StaticCol { name: "ITEM_ID_C", col_type: 11 },
    StaticCol { name: "ITEM_ID_C2", col_type: 11 },
    StaticCol { name: "ITEM_ID_B", col_type: 11 },
    StaticCol { name: "ITEM_ID_B2", col_type: 11 },
    StaticCol { name: "ITEM_ID_A", col_type: 11 },
    StaticCol { name: "ITEM_ID_A2", col_type: 11 },
    StaticCol { name: "ITEM_ID_S", col_type: 11 },
    StaticCol { name: "ITEM_ID_S2", col_type: 11 },
    StaticCol { name: "BILLBOARD", col_type: 11 },
    StaticCol { name: "CPOINT", col_type: 1 },
    StaticCol { name: "BPOINT", col_type: 1 },
    StaticCol { name: "APOINT", col_type: 1 },
    StaticCol { name: "SPOINT", col_type: 1 },
];

static COLS_17: &[StaticCol] = &[
    StaticCol { name: "enum", col_type: 0 },
    StaticCol { name: "name", col_type: 0 },
    StaticCol { name: "ratio", col_type: 10 },
    StaticCol { name: "detail", col_type: 0 },
];

static COLS_18: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "MODEL_NAME", col_type: 0 },
    StaticCol { name: "TEX_NAME", col_type: 0 },
    StaticCol { name: "RANK", col_type: 1 },
    StaticCol { name: "OPEN_FLAG", col_type: 7 },
    StaticCol { name: "GLOW_TYPE", col_type: 10 },
    StaticCol { name: "CONDITION_TYPE", col_type: 10 },
    StaticCol { name: "MAX_LV", col_type: 10 },
    StaticCol { name: "COST_LV10", col_type: 10 },
    StaticCol { name: "COST_LV20", col_type: 10 },
    StaticCol { name: "COST_LV30", col_type: 10 },
    StaticCol { name: "COST_LV40", col_type: 10 },
    StaticCol { name: "BASE_HP", col_type: 10 },
    StaticCol { name: "MAX_HP", col_type: 10 },
    StaticCol { name: "TALK", col_type: 10 },
    StaticCol { name: "TALK_MAX", col_type: 10 },
    StaticCol { name: "PARTY", col_type: 10 },
    StaticCol { name: "PARTY_MAX", col_type: 10 },
    StaticCol { name: "LOVE", col_type: 10 },
    StaticCol { name: "LOVE_MAX", col_type: 10 },
    StaticCol { name: "TECHNIC", col_type: 10 },
    StaticCol { name: "TECHNIC_MAX", col_type: 10 },
    StaticCol { name: "SEXY_BASE", col_type: 10 },
    StaticCol { name: "BEAUTY_BASE", col_type: 10 },
    StaticCol { name: "CUTE_BASE", col_type: 10 },
    StaticCol { name: "FUNNY_BASE", col_type: 10 },
    StaticCol { name: "COMMENT", col_type: 0 },
    StaticCol { name: "VOICE", col_type: 1 },
    StaticCol { name: "SUB_HP", col_type: 10 },
    StaticCol { name: "ADD_HP", col_type: 10 },
];

static COLS_19: &[StaticCol] = &[
    StaticCol { name: "name", col_type: 0 },
    StaticCol { name: "rival_shopname", col_type: 0 },
    StaticCol { name: "rival_owner", col_type: 0 },
    StaticCol { name: "rank", col_type: 3 },
    StaticCol { name: "fan", col_type: 3 },
    StaticCol { name: "explanation", col_type: 0 },
    StaticCol { name: "battle_fan", col_type: 10 },
    StaticCol { name: "battle_start_flag", col_type: 9 },
    StaticCol { name: "battle_finish_flag", col_type: 9 },
    StaticCol { name: "base_money", col_type: 10 },
    StaticCol { name: "battle_name", col_type: 0 },
    StaticCol { name: "battle_detail", col_type: 0 },
    StaticCol { name: "heat_bonus_lv1", col_type: 10 },
    StaticCol { name: "heat_bonus_lv2", col_type: 10 },
    StaticCol { name: "heat_bonus_lv3", col_type: 10 },
    StaticCol { name: "player_heat_bonus_lv1", col_type: 10 },
    StaticCol { name: "player_heat_bonus_lv2", col_type: 10 },
    StaticCol { name: "player_heat_bonus_lv3", col_type: 10 },
    StaticCol { name: "haet_tex", col_type: 0 },
    StaticCol { name: "can_battle_flag", col_type: 9 },
    StaticCol { name: "rival_battle_finish_flag", col_type: 9 },
    StaticCol { name: "guest_num", col_type: 10 },
    StaticCol { name: "set_price", col_type: 10 },
    StaticCol { name: "cast_cost", col_type: 10 },
    StaticCol { name: "present_cost", col_type: 10 },
];

static COLS_20: &[StaticCol] = &[
    StaticCol { name: "area_id", col_type: 10 },
    StaticCol { name: "name", col_type: 0 },
    StaticCol { name: "condition", col_type: 7 },
    StaticCol { name: "fan", col_type: 10 },
    StaticCol { name: "price", col_type: 10 },
];

static COLS_21: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 10 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "ANOTHER_NAME", col_type: 0 },
    StaticCol { name: "", col_type: 2 },
    StaticCol { name: "DESCRIPTION", col_type: 0 },
    StaticCol { name: "STRONG", col_type: 10 },
    StaticCol { name: "RANKING_POINT", col_type: 10 },
    StaticCol { name: "RANKING_POINT_UPPER", col_type: 10 },
    StaticCol { name: "RANKING_POINT_LOWER", col_type: 10 },
    StaticCol { name: "MANNEQUIN_MOTION_START", col_type: 0 },
    StaticCol { name: "MANNEQUIN_MOTION_POSE", col_type: 1 },
    StaticCol { name: "BTL_FLAG", col_type: 7 },
    StaticCol { name: "MODE_BIT_FLAG", col_type: 10 },
];

static COLS_22: &[StaticCol] = &[
    StaticCol { name: "MINIGAME_NAME", col_type: 1 },
    StaticCol { name: "DISP_CONDITION", col_type: 7 },
    StaticCol { name: "BUTTON_MARU", col_type: 1 },
    StaticCol { name: "BUTTON_BATSU", col_type: 1 },
    StaticCol { name: "BUTTON_SANKAKU", col_type: 1 },
    StaticCol { name: "BUTTON_SHIKAKU", col_type: 1 },
    StaticCol { name: "DEGITAL_KEY", col_type: 1 },
    StaticCol { name: "BUTTON_L1", col_type: 1 },
    StaticCol { name: "BUTTON_R1", col_type: 1 },
    StaticCol { name: "BUTTON_L2", col_type: 2 },
    StaticCol { name: "BUTTON_R2", col_type: 2 },
    StaticCol { name: "BUTTON_L3", col_type: 2 },
    StaticCol { name: "BUTTON_R3", col_type: 2 },
    StaticCol { name: "STICK_L", col_type: 1 },
    StaticCol { name: "STICK_R", col_type: 1 },
    StaticCol { name: "SELECT", col_type: 1 },
    StaticCol { name: "START", col_type: 1 },
    StaticCol { name: "TOUCH", col_type: 2 },
];

static COLS_23: &[StaticCol] = &[
    StaticCol { name: "BELONG", col_type: 2 },
    StaticCol { name: "NAME", col_type: 2 },
    StaticCol { name: "WHOLE_TEX_NAME", col_type: 1 },
    StaticCol { name: "SCENARIO_STATE", col_type: 7 },
    StaticCol { name: "TITLE", col_type: 2 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
];

static COLS_24: &[StaticCol] = &[
    StaticCol { name: "ITEM_ID", col_type: 11 },
    StaticCol { name: "TREATING", col_type: 0 },
    StaticCol { name: "POWER", col_type: 0 },
    StaticCol { name: "STABILITY", col_type: 0 },
    StaticCol { name: "REACTOR_ID", col_type: 0 },
    StaticCol { name: "REACTOR_ID2", col_type: 0 },
    StaticCol { name: "COMMENT", col_type: 12 },
];

static COLS_25: &[StaticCol] = &[
    StaticCol { name: "COMMENT", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "LOOK_SCENARIO_STATE", col_type: 9 },
    StaticCol { name: "TITLE", col_type: 0 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
    StaticCol { name: "PICTURE_FILE", col_type: 2 },
];

static COLS_26: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "BASE_ABILITY", col_type: 1 },
    StaticCol { name: "DISTANCE_LIKE_SHORT", col_type: 1 },
    StaticCol { name: "DISTANCE_LIKE_MIDDLE", col_type: 1 },
    StaticCol { name: "DISTANCE_LIKE_LONG", col_type: 1 },
    StaticCol { name: "CONDITION_SCALE_VERY_BAD", col_type: 1 },
    StaticCol { name: "CONDITION_SCALE_BAD", col_type: 1 },
    StaticCol { name: "CONDITION_SCALE_BAD_NORMAL", col_type: 1 },
    StaticCol { name: "CONDITION_SCALE_NORMAL", col_type: 1 },
    StaticCol { name: "CONDITION_SCALE_GOOD_NORMAL", col_type: 1 },
    StaticCol { name: "CONDITION_SCALE_GOOD", col_type: 1 },
    StaticCol { name: "CONDITION_SCALE_VERY_GOOD", col_type: 1 },
    StaticCol { name: "BODY_SCALE", col_type: 1 },
    StaticCol { name: "BODY_COLOR", col_type: 1 },
    StaticCol { name: "PAST_JUNI_1", col_type: 10 },
    StaticCol { name: "PAST_JUNI_2", col_type: 10 },
    StaticCol { name: "PAST_JUNI_3", col_type: 10 },
    StaticCol { name: "PAST_JUNI_4", col_type: 10 },
    StaticCol { name: "PAST_LANE_1", col_type: 10 },
    StaticCol { name: "PAST_LANE_2", col_type: 10 },
    StaticCol { name: "PAST_LANE_3", col_type: 10 },
    StaticCol { name: "PAST_LANE_4", col_type: 10 },
    StaticCol { name: "PAST_CONDITION_1", col_type: 1 },
    StaticCol { name: "PAST_CONDITION_2", col_type: 1 },
    StaticCol { name: "PAST_CONDITION_3", col_type: 1 },
    StaticCol { name: "PAST_CONDITION_4", col_type: 1 },
    StaticCol { name: "PAST_RACE_1", col_type: 1 },
    StaticCol { name: "PAST_RACE_2", col_type: 1 },
    StaticCol { name: "PAST_RACE_3", col_type: 1 },
    StaticCol { name: "PAST_RACE_4", col_type: 1 },
];

static COLS_27: &[StaticCol] = &[
    StaticCol { name: "name", col_type: 0 },
    StaticCol { name: "face0", col_type: 0 },
    StaticCol { name: "face1", col_type: 0 },
    StaticCol { name: "battle_0", col_type: 10 },
    StaticCol { name: "battle_1", col_type: 10 },
    StaticCol { name: "battle_2", col_type: 10 },
    StaticCol { name: "battle_3", col_type: 10 },
    StaticCol { name: "battle_4", col_type: 10 },
    StaticCol { name: "trouble_drink", col_type: 10 },
    StaticCol { name: "trouble_shop", col_type: 10 },
    StaticCol { name: "trouble_play", col_type: 10 },
    StaticCol { name: "trouble_fuzoku", col_type: 10 },
    StaticCol { name: "trouble_campony", col_type: 10 },
    StaticCol { name: "auto_resolve_0", col_type: 10 },
    StaticCol { name: "auto_resolve_1", col_type: 10 },
    StaticCol { name: "auto_resolve_2", col_type: 10 },
    StaticCol { name: "drink_at_min", col_type: 10 },
    StaticCol { name: "drink_at_max", col_type: 10 },
    StaticCol { name: "shop_at_min", col_type: 10 },
    StaticCol { name: "shop_at_max", col_type: 10 },
    StaticCol { name: "play_at_min", col_type: 10 },
    StaticCol { name: "play_at_max", col_type: 10 },
    StaticCol { name: "fuzoku_at_min", col_type: 10 },
    StaticCol { name: "fuzoku_at_max", col_type: 10 },
    StaticCol { name: "company_at_min", col_type: 10 },
    StaticCol { name: "company_at_max", col_type: 10 },
    StaticCol { name: "TIME_1", col_type: 10 },
    StaticCol { name: "TIME_2", col_type: 10 },
    StaticCol { name: "TIME_3", col_type: 10 },
    StaticCol { name: "TIME_4", col_type: 10 },
    StaticCol { name: "TIME_5", col_type: 10 },
];

static COLS_28: &[StaticCol] = &[
    StaticCol { name: "id", col_type: 3 },
    StaticCol { name: "name", col_type: 0 },
    StaticCol { name: "shoptype", col_type: 4 },
    StaticCol { name: "condition", col_type: 7 },
    StaticCol { name: "pin", col_type: 10 },
    StaticCol { name: "picture", col_type: 0 },
    StaticCol { name: "profit_d", col_type: 0 },
    StaticCol { name: "profit_c", col_type: 0 },
    StaticCol { name: "profit_b", col_type: 0 },
    StaticCol { name: "profit_a", col_type: 0 },
    StaticCol { name: "profit_s", col_type: 0 },
    StaticCol { name: "share_d", col_type: 4 },
    StaticCol { name: "share_c", col_type: 4 },
    StaticCol { name: "share_b", col_type: 4 },
    StaticCol { name: "share_a", col_type: 4 },
    StaticCol { name: "share_s", col_type: 4 },
    StaticCol { name: "init_exp", col_type: 4 },
    StaticCol { name: "exp_c", col_type: 4 },
    StaticCol { name: "exp_b", col_type: 4 },
    StaticCol { name: "exp_a", col_type: 4 },
    StaticCol { name: "exp_s", col_type: 4 },
    StaticCol { name: "price", col_type: 1 },
    StaticCol { name: "price_d", col_type: 1 },
    StaticCol { name: "price_c", col_type: 1 },
    StaticCol { name: "price_b", col_type: 1 },
    StaticCol { name: "price_a", col_type: 1 },
    StaticCol { name: "price_s", col_type: 1 },
    StaticCol { name: "lost_setting", col_type: 7 },
];

static COLS_29: &[StaticCol] = &[
    StaticCol { name: "id", col_type: 3 },
    StaticCol { name: "name", col_type: 0 },
    StaticCol { name: "post", col_type: 1 },
    StaticCol { name: "salary", col_type: 4 },
    StaticCol { name: "comment", col_type: 0 },
    StaticCol { name: "ability_rank", col_type: 4 },
    StaticCol { name: "param_1", col_type: 1 },
    StaticCol { name: "param_2", col_type: 1 },
    StaticCol { name: "param_3", col_type: 1 },
    StaticCol { name: "param_4", col_type: 1 },
    StaticCol { name: "param_5", col_type: 1 },
    StaticCol { name: "face_picture", col_type: 0 },
    StaticCol { name: "is_possible", col_type: 7 },
    StaticCol { name: "model_name", col_type: 0 },
    StaticCol { name: "npc_ratio", col_type: 10 },
];

static COLS_30: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "CAN_INTERRUPT", col_type: 1 },
    StaticCol { name: "PRIORITY", col_type: 1 },
    StaticCol { name: "EXPIRE_FRAME", col_type: 2 },
    StaticCol { name: "WAIT_FRAME", col_type: 2 },
    StaticCol { name: "DISABLE_FRAME", col_type: 2 },
];

static COLS_31: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "POPUP", col_type: 1 },
    StaticCol { name: "SOUND_ID", col_type: 1 },
];

static COLS_32: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "SOUND_ID", col_type: 0 },
    StaticCol { name: "WAIT_TIME", col_type: 1 },
];

static COLS_33: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "CAN_INTERRUPT", col_type: 2 },
    StaticCol { name: "PRIORITY", col_type: 1 },
    StaticCol { name: "PREFER", col_type: 1 },
    StaticCol { name: "EXPIRE_TIME", col_type: 1 },
    StaticCol { name: "WAIT_TIME", col_type: 1 },
    StaticCol { name: "DISABLE_TIME", col_type: 2 },
    StaticCol { name: "CONDITION", col_type: 2 },
    StaticCol { name: "INSERT_CAR_NAME", col_type: 2 },
    StaticCol { name: "USE_DEFAULT", col_type: 1 },
];

static COLS_34: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "CAN_INTERRUPT", col_type: 1 },
    StaticCol { name: "PRIORITY", col_type: 1 },
    StaticCol { name: "EXPIRE_TIME", col_type: 1 },
    StaticCol { name: "WAIT_TIME", col_type: 1 },
    StaticCol { name: "DISABLE_TIME", col_type: 2 },
];

static COLS_35: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "POPUP", col_type: 1 },
    StaticCol { name: "SOUND_ID", col_type: 1 },
    StaticCol { name: "WAIT_FRAME", col_type: 1 },
];

static COLS_36: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "SOUND_ID", col_type: 0 },
    StaticCol { name: "TALKER_MOTION", col_type: 1 },
    StaticCol { name: "LISTENER_MOTION_1", col_type: 1 },
    StaticCol { name: "LISTENER_MOTION_2", col_type: 1 },
    StaticCol { name: "LISTENER_MOTION_3", col_type: 1 },
    StaticCol { name: "WAIT_TIME", col_type: 2 },
    StaticCol { name: "LOOK_TARGET", col_type: 1 },
    StaticCol { name: "EMOTION", col_type: 1 },
];

static COLS_37: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "TYPE", col_type: 1 },
    StaticCol { name: "SPEAK_ID", col_type: 1 },
    StaticCol { name: "LAST_NAME", col_type: 1 },
    StaticCol { name: "FIRST_NAME", col_type: 1 },
    StaticCol { name: "INIT_TENSION", col_type: 1 },
    StaticCol { name: "INIT_CHIP", col_type: 1 },
    StaticCol { name: "DO_NOTHING_PERCENT", col_type: 1 },
    StaticCol { name: "TOTAL_BET_PER_TURN0", col_type: 1 },
    StaticCol { name: "TOTAL_BET_PER_TURN1", col_type: 1 },
    StaticCol { name: "TOTAL_BET_PER_TURN2", col_type: 1 },
    StaticCol { name: "TOTAL_BET_PER_TURN3", col_type: 1 },
    StaticCol { name: "TOTAL_BET_PER_TURN4", col_type: 1 },
    StaticCol { name: "BET_TO_NUMBER_NUM", col_type: 0 },
    StaticCol { name: "BET_TO_NOT_NUMBER_NUM", col_type: 1 },
    StaticCol { name: "BET_WAIT_FRAME", col_type: 1 },
    StaticCol { name: "CURSOR_WAIT_FRAME", col_type: 1 },
    StaticCol { name: "VOICE_KIND", col_type: 0 },
];

static COLS_38: &[StaticCol] = &[
    StaticCol { name: "START_SCENARIO_STATE", col_type: 7 },
    StaticCol { name: "ENCOUNT_LV", col_type: 10 },
    StaticCol { name: "ENCOUNT_LV_LOW", col_type: 10 },
    StaticCol { name: "ENCOUNT_LV_HIGH", col_type: 10 },
    StaticCol { name: "ENEMY_NUM_MIN", col_type: 10 },
    StaticCol { name: "ENEMY_NUM_MAX", col_type: 10 },
    StaticCol { name: "STYLE_RATIO_NML", col_type: 10 },
    StaticCol { name: "STYLE_RATIO_FAT", col_type: 10 },
    StaticCol { name: "STYLE_RATIO_MUS", col_type: 10 },
    StaticCol { name: "STYLE_RATIO_NMLFAT", col_type: 10 },
    StaticCol { name: "STYLE_RATIO_NMLMUS", col_type: 10 },
    StaticCol { name: "STYLE_RATIO_FATMUS", col_type: 10 },
    StaticCol { name: "STYLE_RATIO_ALL", col_type: 10 },
    StaticCol { name: "POCKET_RATIO", col_type: 10 },
];

static COLS_39: &[StaticCol] = &[
    StaticCol { name: "LOCATION", col_type: 2 },
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "LV", col_type: 4 },
    StaticCol { name: "COST", col_type: 4 },
    StaticCol { name: "MAX_NUM", col_type: 4 },
    StaticCol { name: "RATIO_BARGAIN", col_type: 4 },
    StaticCol { name: "RATIO_FIX", col_type: 4 },
    StaticCol { name: "RATIO_TREASURE", col_type: 4 },
    StaticCol { name: "RARE_ARMS_1", col_type: 4 },
    StaticCol { name: "RARE_ARMS_2", col_type: 4 },
    StaticCol { name: "RARE_ARMS_3", col_type: 4 },
    StaticCol { name: "RARE_ARMS_4", col_type: 4 },
    StaticCol { name: "RARE_ARMS_5", col_type: 4 },
    StaticCol { name: "RARE_ARMS_6", col_type: 4 },
    StaticCol { name: "RARE_ARMS_7", col_type: 4 },
    StaticCol { name: "RARE_ARMS_8", col_type: 4 },
    StaticCol { name: "RARE_ARMS_9", col_type: 4 },
    StaticCol { name: "RARE_ARMS_10", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_1", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_2", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_3", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_4", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_5", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_6", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_7", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_8", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_9", col_type: 4 },
    StaticCol { name: "RARE_MATERIAL_10", col_type: 4 },
    StaticCol { name: "SPECIALTY_KIND", col_type: 1 },
    StaticCol { name: "FIX_ITEM", col_type: 11 },
    StaticCol { name: "OPEN", col_type: 7 },
    StaticCol { name: "HINT", col_type: 0 },
    StaticCol { name: "PICTURE", col_type: 0 },
];

static COLS_40: &[StaticCol] = &[
    StaticCol { name: "FLAG", col_type: 7 },
    StaticCol { name: "RATIO", col_type: 3 },
];

static COLS_41: &[StaticCol] = &[
    StaticCol { name: "KIND_ID", col_type: 2 },
    StaticCol { name: "KIND_NAME", col_type: 2 },
    StaticCol { name: "ITEM", col_type: 11 },
];

static COLS_42: &[StaticCol] = &[
    StaticCol { name: "LOCATION", col_type: 2 },
    StaticCol { name: "LOCATION_HINT", col_type: 2 },
    StaticCol { name: "LOCATION_PICTURE", col_type: 2 },
    StaticCol { name: "LOCATION_OPEN", col_type: 7 },
    StaticCol { name: "ORGANIZATION", col_type: 0 },
    StaticCol { name: "RANK", col_type: 4 },
    StaticCol { name: "BUDGET", col_type: 4 },
    StaticCol { name: "AGENT1", col_type: 1 },
    StaticCol { name: "AGENT2", col_type: 1 },
    StaticCol { name: "AGENT3", col_type: 1 },
    StaticCol { name: "AGENT4", col_type: 1 },
    StaticCol { name: "AGENT5", col_type: 1 },
    StaticCol { name: "RARE1", col_type: 4 },
    StaticCol { name: "RARE2", col_type: 4 },
    StaticCol { name: "RARE3", col_type: 4 },
    StaticCol { name: "RARE4", col_type: 4 },
    StaticCol { name: "RARE5", col_type: 4 },
    StaticCol { name: "RARE6", col_type: 4 },
    StaticCol { name: "RARE7", col_type: 4 },
    StaticCol { name: "RARE8", col_type: 4 },
    StaticCol { name: "RARE9", col_type: 4 },
    StaticCol { name: "RARE10", col_type: 4 },
    StaticCol { name: "TREASURE", col_type: 11 },
    StaticCol { name: "LOTTERY_KIND_1", col_type: 1 },
    StaticCol { name: "LOTTERY_KIND_2", col_type: 1 },
    StaticCol { name: "LOTTERY_KIND_3", col_type: 1 },
    StaticCol { name: "LOTTERY_KIND_4", col_type: 1 },
    StaticCol { name: "LOTTERY_KIND_5", col_type: 1 },
    StaticCol { name: "LOTTERY_KIND_6", col_type: 1 },
    StaticCol { name: "ORGANIZATION_OPEN", col_type: 7 },
    StaticCol { name: "ORGANIZATION_HINT", col_type: 1 },
    StaticCol { name: "ORGANIZATION_PICTURE", col_type: 0 },
    StaticCol { name: "RESULT1_TEXT_TEXTURE", col_type: 0 },
    StaticCol { name: "RESULT1_TEXT_SUBTITLE", col_type: 1 },
    StaticCol { name: "RESULT2_TEXT_TEXTURE", col_type: 0 },
    StaticCol { name: "RESULT2_TEXT_SUBTITLE", col_type: 1 },
    StaticCol { name: "RESULT1_BG_TEXTURE", col_type: 1 },
    StaticCol { name: "RESULT2_BG_TEXTURE", col_type: 1 },
];

static COLS_43: &[StaticCol] = &[
    StaticCol { name: "KIND", col_type: 2 },
    StaticCol { name: "TEXT_TEXTURE", col_type: 0 },
    StaticCol { name: "TEXT_SUBTITLE", col_type: 0 },
    StaticCol { name: "BG_TEXTURE", col_type: 1 },
];

static COLS_44: &[StaticCol] = &[
    StaticCol { name: "PROFILE", col_type: 0 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "EXP", col_type: 1 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "TITLE", col_type: 0 },
    StaticCol { name: "TEXT", col_type: 0 },
    StaticCol { name: "PICT_FNAME", col_type: 1 },
    StaticCol { name: "CORRECT_NUM", col_type: 1 },
];

static COLS_45: &[StaticCol] = &[
    StaticCol { name: "NUMBER", col_type: 10 },
    StaticCol { name: "ZAKO", col_type: 10 },
    StaticCol { name: "RARE", col_type: 10 },
    StaticCol { name: "SUPER_RARE", col_type: 10 },
];

static COLS_46: &[StaticCol] = &[
    StaticCol { name: "TYPE", col_type: 0 },
    StaticCol { name: "TITLE", col_type: 1 },
    StaticCol { name: "STR", col_type: 0 },
    StaticCol { name: "TIME", col_type: 1 },
];

static COLS_47: &[StaticCol] = &[
    StaticCol { name: "stage", col_type: 1 },
    StaticCol { name: "stage_enum", col_type: 1 },
    StaticCol { name: "rule", col_type: 1 },
    StaticCol { name: "rule_enum", col_type: 1 },
    StaticCol { name: "style", col_type: 1 },
    StaticCol { name: "style_enum", col_type: 1 },
    StaticCol { name: "player_type", col_type: 1 },
    StaticCol { name: "price", col_type: 1 },
    StaticCol { name: "open_flag", col_type: 7 },
];

static COLS_48: &[StaticCol] = &[
    StaticCol { name: "ENUM", col_type: 0 },
    StaticCol { name: "NAME", col_type: 12 },
    StaticCol { name: "DISP_NUMBER", col_type: 1 },
    StaticCol { name: "START_CONDITION", col_type: 7 },
    StaticCol { name: "SUCCESS", col_type: 9 },
    StaticCol { name: "FINISH_SCENARIOSTATE", col_type: 9 },
    StaticCol { name: "FAILURE", col_type: 2 },
    StaticCol { name: "EXEC_NUM", col_type: 1 },
    StaticCol { name: "FINISH", col_type: 1 },
    StaticCol { name: "NUM_DISP", col_type: 1 },
    StaticCol { name: "DISP_ENEMY_GAUGE", col_type: 1 },
    StaticCol { name: "DETAIL_EXPLAIN", col_type: 0 },
    StaticCol { name: "EXPLAIN", col_type: 1 },
    StaticCol { name: "HUMAN_FREEZE", col_type: 2 },
    StaticCol { name: "PICTURE", col_type: 1 },
    StaticCol { name: "PLAYER_NO_DEAD", col_type: 10 },
    StaticCol { name: "ENEMY_NO_DEAD", col_type: 10 },
    StaticCol { name: "HEAT_GAUGE_MAX", col_type: 10 },
    StaticCol { name: "HEAT_GAUGE_ZERO", col_type: 10 },
    StaticCol { name: "STYLE_CHANGE_DISABLE", col_type: 10 },
    StaticCol { name: "MONEY_DISABLE", col_type: 10 },
];

static COLS_49: &[StaticCol] = &[
    StaticCol { name: "CATEGORY", col_type: 2 },
    StaticCol { name: "CATEGORY_EXP", col_type: 2 },
    StaticCol { name: "OPEN_CONDITION", col_type: 7 },
    StaticCol { name: "MENU_NAME", col_type: 1 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "EXPLANATION", col_type: 1 },
    StaticCol { name: "LEVEL_DISP", col_type: 1 },
    StaticCol { name: "LEVEL", col_type: 1 },
    StaticCol { name: "EQUIP_ID", col_type: 11 },
    StaticCol { name: "CHAPTER", col_type: 1 },
    StaticCol { name: "SCENARIO", col_type: 0 },
    StaticCol { name: "ENEMY_NUM", col_type: 2 },
];

static COLS_50: &[StaticCol] = &[
    StaticCol { name: "CHARA_STATE", col_type: 7 },
    StaticCol { name: "OPEN_STATE", col_type: 7 },
    StaticCol { name: "CATEGORY", col_type: 1 },
    StaticCol { name: "FUNCTION_NAME", col_type: 1 },
    StaticCol { name: "GET_SCENARIO_STATE", col_type: 9 },
    StaticCol { name: "GET_ITEM_ID", col_type: 11 },
    StaticCol { name: "FUNCTION_DETAIL", col_type: 1 },
    StaticCol { name: "USE_VIRTUE", col_type: 10 },
    StaticCol { name: "IS_GACHA", col_type: 10 },
];

static COLS_51: &[StaticCol] = &[
    StaticCol { name: "name", col_type: 0 },
    StaticCol { name: "singer", col_type: 0 },
    StaticCol { name: "file", col_type: 0 },
    StaticCol { name: "buy_cd", col_type: 10 },
    StaticCol { name: "buy_walkman", col_type: 10 },
];

static COLS_52: &[StaticCol] = &[
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "CATEGORY", col_type: 2 },
    StaticCol { name: "SKILL", col_type: 0 },
    StaticCol { name: "TAG", col_type: 1 },
    StaticCol { name: "MONEY", col_type: 10 },
    StaticCol { name: "MOVE_METHOD", col_type: 1 },
    StaticCol { name: "BEFORE_SKILL_VALUE", col_type: 10 },
    StaticCol { name: "DEGITAL_UP", col_type: 10 },
    StaticCol { name: "DEGITAL_DOWN", col_type: 10 },
    StaticCol { name: "DEGITAL_LEFT", col_type: 10 },
    StaticCol { name: "DEGITAL_RIGHT", col_type: 10 },
    StaticCol { name: "SEAL_RELEASE_SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "NEED_SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
    StaticCol { name: "CONTROL_EXPLANATION", col_type: 1 },
    StaticCol { name: "PICT_FNAME", col_type: 0 },
    StaticCol { name: "LEARN_EXPLANATION", col_type: 2 },
    StaticCol { name: "USE_HEAT", col_type: 2 },
    StaticCol { name: "USE_RED_HEAT", col_type: 1 },
    StaticCol { name: "HEAT_EXPLAIN", col_type: 1 },
    StaticCol { name: "HEAT_CONDITION", col_type: 1 },
    StaticCol { name: "HEAT_PICTURE", col_type: 2 },
    StaticCol { name: "BEFORE_LEARN", col_type: 1 },
    StaticCol { name: "taikenkai", col_type: 10 },
    StaticCol { name: "PICT_FNAME_VITA", col_type: 2 },
    StaticCol { name: "sort", col_type: 10 },
];

static COLS_53: &[StaticCol] = &[
    StaticCol { name: "level", col_type: 0 },
    StaticCol { name: "need_experience_kiryu", col_type: 1 },
    StaticCol { name: "add_hit_point_kiryu", col_type: 1 },
    StaticCol { name: "add_heat_gauge_kiryu", col_type: 1 },
    StaticCol { name: "add_skillsoul_kiryu", col_type: 1 },
    StaticCol { name: "neet_heat", col_type: 2 },
];

static COLS_54: &[StaticCol] = &[
    StaticCol { name: "ACTION_SET_NAME", col_type: 0 },
    StaticCol { name: "SOUND_NAME", col_type: 0 },
];

static COLS_55: &[StaticCol] = &[
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "PLAYER_ROT_Y", col_type: 0 },
    StaticCol { name: "CAM_X", col_type: 0 },
    StaticCol { name: "CAM_Y", col_type: 0 },
    StaticCol { name: "CAM_Z", col_type: 0 },
    StaticCol { name: "CAM_INTR_X", col_type: 0 },
    StaticCol { name: "CAM_INTR_Y", col_type: 0 },
    StaticCol { name: "CAM_INTR_Z", col_type: 0 },
    StaticCol { name: "OPEN_CLOSE", col_type: 9 },
    StaticCol { name: "NPC_X", col_type: 2 },
    StaticCol { name: "NPC_Y", col_type: 2 },
    StaticCol { name: "NPC_Z", col_type: 2 },
    StaticCol { name: "NPC_ROTY", col_type: 2 },
];

static COLS_56: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "MULTI", col_type: 10 },
];

static COLS_57: &[StaticCol] = &[
    StaticCol { name: "DECK_ENUM", col_type: 0 },
    StaticCol { name: "DECK_NAME", col_type: 0 },
    StaticCol { name: "FIXED", col_type: 2 },
    StaticCol { name: "CARD1", col_type: 1 },
    StaticCol { name: "CARD2", col_type: 1 },
    StaticCol { name: "CARD3", col_type: 1 },
    StaticCol { name: "CARD4", col_type: 1 },
    StaticCol { name: "CARD5", col_type: 1 },
    StaticCol { name: "MONEY", col_type: 10 },
    StaticCol { name: "ITEM_ID", col_type: 11 },
    StaticCol { name: "RANK", col_type: 10 },
];

static COLS_58: &[StaticCol] = &[
    StaticCol { name: "STYLE", col_type: 0 },
    StaticCol { name: "GEAR1", col_type: 10 },
    StaticCol { name: "GEAR2", col_type: 10 },
    StaticCol { name: "GEAR3", col_type: 10 },
    StaticCol { name: "GEAR4", col_type: 10 },
    StaticCol { name: "GEAR5", col_type: 10 },
];

static COLS_59: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "PARAM", col_type: 10 },
    StaticCol { name: "STRING", col_type: 2 },
];

static COLS_60: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 2 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "WEATHER", col_type: 2 },
    StaticCol { name: "DRIVE_MISSION", col_type: 2 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "BATTLE_TYPE", col_type: 0 },
];

static COLS_61: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 1 },
    StaticCol { name: "START_SCENARIO_STATE", col_type: 7 },
    StaticCol { name: "FINISH_SCENARIO_STATE", col_type: 9 },
    StaticCol { name: "CAPTION_NAME", col_type: 1 },
    StaticCol { name: "EMBLEM_NAME", col_type: 2 },
    StaticCol { name: "SUBTITLE", col_type: 1 },
    StaticCol { name: "PLAY_SCENE", col_type: 1 },
    StaticCol { name: "BLUR_START", col_type: 10 },
    StaticCol { name: "BLUR_END", col_type: 10 },
];

static COLS_62: &[StaticCol] = &[
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "TYPE", col_type: 1 },
    StaticCol { name: "START_CAMERA_NAME", col_type: 2 },
    StaticCol { name: "START_CAMERA_DEGREE", col_type: 4 },
    StaticCol { name: "START_CAMERA_PARAM", col_type: 3 },
    StaticCol { name: "NAME_ENEMY", col_type: 0 },
    StaticCol { name: "IS_POLICE_CHASE", col_type: 2 },
    StaticCol { name: "IS_LAP_ENABLED", col_type: 2 },
    StaticCol { name: "LAP_NUM", col_type: 4 },
    StaticCol { name: "CHECK_POINT_NUM", col_type: 4 },
    StaticCol { name: "CAN_PLAYER_HACT", col_type: 2 },
    StaticCol { name: "IS_DAMAGE_WALK_ENABLED", col_type: 5 },
    StaticCol { name: "ENABLE_DISTANCE_FINISH", col_type: 1 },
    StaticCol { name: "DISTANCE_TOO_PARTING", col_type: 4 },
    StaticCol { name: "SCENARIO_STATUS_GAUGE_DISP", col_type: 7 },
    StaticCol { name: "IS_TIME_DISP", col_type: 2 },
    StaticCol { name: "CATEGORY", col_type: 2 },
    StaticCol { name: "SELECT_EXPLANATION", col_type: 2 },
    StaticCol { name: "NO_TACKLE", col_type: 2 },
    StaticCol { name: "KEEP_KIRYU_HP", col_type: 2 },
    StaticCol { name: "FACE_TEXTURE", col_type: 1 },
    StaticCol { name: "AREA_CHANGE", col_type: 2 },
    StaticCol { name: "SIGNAL_CONTROL", col_type: 2 },
];

static COLS_63: &[StaticCol] = &[
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "WHO", col_type: 1 },
    StaticCol { name: "CONDITION", col_type: 1 },
    StaticCol { name: "VALUE", col_type: 1 },
];

static COLS_64: &[StaticCol] = &[
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "TYPE", col_type: 1 },
    StaticCol { name: "PROJECT_PATH", col_type: 1 },
];

static COLS_65: &[StaticCol] = &[
    StaticCol { name: "EVENT_ENUM", col_type: 0 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
];

static COLS_66: &[StaticCol] = &[
    StaticCol { name: "CATEGORY", col_type: 2 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
];

static COLS_67: &[StaticCol] = &[
    StaticCol { name: "CATEGORY", col_type: 1 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
];

static COLS_68: &[StaticCol] = &[
    StaticCol { name: "CHAPTER", col_type: 1 },
    StaticCol { name: "SCENARIO", col_type: 0 },
    StaticCol { name: "NAME", col_type: 1 },
    StaticCol { name: "COMMENT", col_type: 12 },
];

static COLS_69: &[StaticCol] = &[
    StaticCol { name: "WORD", col_type: 0 },
    StaticCol { name: "YOMIGANA", col_type: 0 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
    StaticCol { name: "SEARCH_KEY", col_type: 0 },
];

static COLS_70: &[StaticCol] = &[
    StaticCol { name: "IGNORE_WORD", col_type: 0 },
];

static COLS_71: &[StaticCol] = &[
    StaticCol { name: "EID_BEFORE", col_type: 0 },
    StaticCol { name: "EID_AFTER", col_type: 0 },
];

static COLS_72: &[StaticCol] = &[
    StaticCol { name: "EID_BEFORE", col_type: 0 },
    StaticCol { name: "EID_AFTER", col_type: 0 },
];

static COLS_73: &[StaticCol] = &[
    StaticCol { name: "REWARD_ID", col_type: 2 },
    StaticCol { name: "ITEM", col_type: 11 },
    StaticCol { name: "RATIO", col_type: 1 },
    StaticCol { name: "OPEN", col_type: 7 },
];

static COLS_74: &[StaticCol] = &[
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "WEATHER", col_type: 1 },
    StaticCol { name: "DAYNIGHT", col_type: 1 },
];

static COLS_75: &[StaticCol] = &[
    StaticCol { name: "SKILL", col_type: 0 },
    StaticCol { name: "EXP_KRU", col_type: 9 },
    StaticCol { name: "EXP_KRS1", col_type: 9 },
    StaticCol { name: "EXP_KRS2", col_type: 9 },
    StaticCol { name: "EXP_KRS3", col_type: 9 },
    StaticCol { name: "EXP_KRS4", col_type: 9 },
    StaticCol { name: "EXP_KRS5", col_type: 9 },
    StaticCol { name: "EXP_KRH1", col_type: 9 },
    StaticCol { name: "EXP_KRH2", col_type: 9 },
    StaticCol { name: "EXP_KRH3", col_type: 9 },
    StaticCol { name: "EXP_KRH4", col_type: 9 },
    StaticCol { name: "EXP_KRH5", col_type: 9 },
    StaticCol { name: "EXP_KRP1", col_type: 9 },
    StaticCol { name: "EXP_KRP2", col_type: 9 },
    StaticCol { name: "EXP_KRP3", col_type: 9 },
    StaticCol { name: "EXP_KRP4", col_type: 9 },
    StaticCol { name: "EXP_KRP5", col_type: 9 },
    StaticCol { name: "EXP_KRL1", col_type: 9 },
    StaticCol { name: "EXP_KRL2", col_type: 9 },
    StaticCol { name: "EXP_KRL3", col_type: 9 },
    StaticCol { name: "EXP_KRL4", col_type: 9 },
    StaticCol { name: "EXP_KRL5", col_type: 9 },
    StaticCol { name: "EXP_MJM", col_type: 9 },
    StaticCol { name: "EXP_MJA1", col_type: 9 },
    StaticCol { name: "EXP_MJA2", col_type: 9 },
    StaticCol { name: "EXP_MJA3", col_type: 9 },
    StaticCol { name: "EXP_MJA4", col_type: 9 },
    StaticCol { name: "EXP_MJA5", col_type: 9 },
    StaticCol { name: "EXP_MJD1", col_type: 9 },
    StaticCol { name: "EXP_MJD2", col_type: 9 },
    StaticCol { name: "EXP_MJD3", col_type: 9 },
    StaticCol { name: "EXP_MJD4", col_type: 9 },
    StaticCol { name: "EXP_MJD5", col_type: 9 },
    StaticCol { name: "EXP_MJW1", col_type: 9 },
    StaticCol { name: "EXP_MJW2", col_type: 9 },
    StaticCol { name: "EXP_MJW3", col_type: 9 },
    StaticCol { name: "EXP_MJW4", col_type: 9 },
    StaticCol { name: "EXP_MJW5", col_type: 9 },
    StaticCol { name: "EXP_MJL1", col_type: 9 },
    StaticCol { name: "EXP_MJL2", col_type: 9 },
    StaticCol { name: "EXP_MJL3", col_type: 9 },
    StaticCol { name: "EXP_MJL4", col_type: 9 },
    StaticCol { name: "EXP_MJL5", col_type: 9 },
];

static COLS_76: &[StaticCol] = &[
    StaticCol { name: "TITLE", col_type: 2 },
    StaticCol { name: "SCENARIO", col_type: 6 },
    StaticCol { name: "EXPLANATION", col_type: 1 },
    StaticCol { name: "TABAKO_EXPLANATION", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "FINISH_FLAG", col_type: 2 },
];

static COLS_77: &[StaticCol] = &[
    StaticCol { name: "TITLE", col_type: 2 },
    StaticCol { name: "PLACE", col_type: 2 },
    StaticCol { name: "SCENARIO", col_type: 6 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
    StaticCol { name: "TABAKO_EXPLANATION", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "FINISH_FLAG", col_type: 1 },
    StaticCol { name: "STAGE_ID", col_type: 8 },
    StaticCol { name: "START_POINTS", col_type: 2 },
    StaticCol { name: "DISP_MISSION_NUMBER", col_type: 10 },
];

static COLS_78: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 2 },
    StaticCol { name: "SEQUENCE_ID", col_type: 0 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 2 },
    StaticCol { name: "DRIVE_MISSION", col_type: 2 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "GAME_LIVE_STREAMING_ENABLED", col_type: 1 },
    StaticCol { name: "GAME_LIVE_STREAMING_PERMIT", col_type: 1 },
];

static COLS_79: &[StaticCol] = &[
    StaticCol { name: "HACTID", col_type: 0 },
    StaticCol { name: "ATTR_BUKI", col_type: 1 },
];

static COLS_80: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "VALUE", col_type: 10 },
];

static COLS_81: &[StaticCol] = &[
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "REGION_TOKYO", col_type: 2 },
    StaticCol { name: "REGION_OSAKA", col_type: 2 },
    StaticCol { name: "REGION_SAPPORO", col_type: 2 },
    StaticCol { name: "REGION_NAGOYA", col_type: 2 },
    StaticCol { name: "REGION_FUKUOKA", col_type: 2 },
    StaticCol { name: "REGION_OTHER", col_type: 2 },
    StaticCol { name: "KIRYU_MODEL", col_type: 1 },
    StaticCol { name: "PLAYER_TYPE", col_type: 1 },
];

static COLS_82: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 0 },
    StaticCol { name: "KIND", col_type: 1 },
    StaticCol { name: "NAME", col_type: 0 },
    StaticCol { name: "CATEGORY_RECOVER", col_type: 1 },
    StaticCol { name: "CATEGORY_EQUIP", col_type: 1 },
    StaticCol { name: "CATEGORY_ETC", col_type: 1 },
    StaticCol { name: "SERIES_NUMBER", col_type: 4 },
    StaticCol { name: "IN_SERIES_NUMBER", col_type: 4 },
    StaticCol { name: "HIRAGANA", col_type: 0 },
    StaticCol { name: "EXPLANATION", col_type: 0 },
    StaticCol { name: "BUY", col_type: 3 },
    StaticCol { name: "SELL", col_type: 4 },
    StaticCol { name: "UNIT", col_type: 2 },
    StaticCol { name: "IMPORTANT", col_type: 2 },
    StaticCol { name: "PRESENT", col_type: 1 },
    StaticCol { name: "RECOVER_HP", col_type: 4 },
    StaticCol { name: "RECOVER_HEAT", col_type: 5 },
    StaticCol { name: "EXPERIENCE", col_type: 5 },
    StaticCol { name: "MONEY", col_type: 5 },
    StaticCol { name: "MONEY_SCALE", col_type: 2 },
    StaticCol { name: "INTOXICATION", col_type: 5 },
    StaticCol { name: "FOOD_SE", col_type: 1 },
    StaticCol { name: "EQUIP", col_type: 2 },
    StaticCol { name: "ICON", col_type: 0 },
    StaticCol { name: "PICT", col_type: 2 },
    StaticCol { name: "ARMS_ID", col_type: 0 },
    StaticCol { name: "PHYSICAL_STRENGTH", col_type: 5 },
    StaticCol { name: "CONCENTRATION", col_type: 5 },
    StaticCol { name: "FIGHT", col_type: 5 },
    StaticCol { name: "DEFENCE", col_type: 5 },
    StaticCol { name: "DEFENCE_IMPACT", col_type: 5 },
    StaticCol { name: "DEFENCE_CUTLERY", col_type: 5 },
    StaticCol { name: "DEFENCE_BULLET", col_type: 5 },
    StaticCol { name: "DEFENCE_FLAME", col_type: 5 },
    StaticCol { name: "DEFENCE_EXPLOSION", col_type: 5 },
    StaticCol { name: "MORE_EXPLANATION1", col_type: 2 },
    StaticCol { name: "MORE_EXPLANATION2", col_type: 2 },
    StaticCol { name: "MORE_EXPLANATION3", col_type: 2 },
    StaticCol { name: "MORE_EXPLANATION4", col_type: 2 },
    StaticCol { name: "MORE_EXPLANATION5", col_type: 2 },
    StaticCol { name: "MORE_EXPLANATION6", col_type: 2 },
    StaticCol { name: "MORE_EXPLANATION7", col_type: 2 },
    StaticCol { name: "MORE_EXPLANATION8", col_type: 2 },
    StaticCol { name: "SKILL_LEVEL", col_type: 2 },
    StaticCol { name: "RARE", col_type: 4 },
    StaticCol { name: "INSTANT_USE", col_type: 2 },
    StaticCol { name: "WAREHOUSE_COLLECTIBLE_NUM", col_type: 4 },
    StaticCol { name: "CARRY_ITEM_COLLECTIBLE_NUM", col_type: 4 },
    StaticCol { name: "ROB_ARMS_ID", col_type: 2 },
    StaticCol { name: "GET_SCENARIO_FLAG", col_type: 7 },
    StaticCol { name: "MARK_1", col_type: 2 },
    StaticCol { name: "MARK_2", col_type: 2 },
    StaticCol { name: "MARK_3", col_type: 2 },
];

static COLS_83: &[StaticCol] = &[
    StaticCol { name: "ITEM_ALIAS", col_type: 0 },
    StaticCol { name: "ITEM_ID", col_type: 11 },
    StaticCol { name: "NAME", col_type: 0 },
];

static COLS_84: &[StaticCol] = &[
    StaticCol { name: "enum", col_type: 0 },
    StaticCol { name: "category", col_type: 1 },
    StaticCol { name: "mark", col_type: 0 },
    StaticCol { name: "hint", col_type: 1 },
    StaticCol { name: "comment", col_type: 12 },
    StaticCol { name: "param", col_type: 4 },
];

static COLS_85: &[StaticCol] = &[
    StaticCol { name: "ID", col_type: 11 },
    StaticCol { name: "max_power0", col_type: 4 },
    StaticCol { name: "max_power1", col_type: 4 },
    StaticCol { name: "max_power2", col_type: 4 },
    StaticCol { name: "max_power3", col_type: 4 },
    StaticCol { name: "max_power4", col_type: 4 },
    StaticCol { name: "defence", col_type: 5 },
    StaticCol { name: "slot_num", col_type: 4 },
    StaticCol { name: "mark", col_type: 1 },
];

static COLS_86: &[StaticCol] = &[
    StaticCol { name: "KIYAKU_TITLE", col_type: 1 },
    StaticCol { name: "KIYAKU_SENTENCE", col_type: 0 },
];

static COLS_87: &[StaticCol] = &[
    StaticCol { name: "get_money", col_type: 2 },
    StaticCol { name: "name", col_type: 0 },
    StaticCol { name: "base_unit", col_type: 10 },
    StaticCol { name: "unit", col_type: 2 },
    StaticCol { name: "base_unit_str", col_type: 0 },
    StaticCol { name: "rand", col_type: 10 },
];

static COLS_88: &[StaticCol] = &[
    StaticCol { name: "LOOPID", col_type: 0 },
    StaticCol { name: "ENDID", col_type: 2 },
];

static COLS_89: &[StaticCol] = &[
    StaticCol { name: "MOTION_ID", col_type: 0 },
];

static COLS_90: &[StaticCol] = &[
    StaticCol { name: "id", col_type: 3 },
    StaticCol { name: "name", col_type: 3 },
    StaticCol { name: "ScenarioFlag", col_type: 9 },
    StaticCol { name: "max_level", col_type: 4 },
    StaticCol { name: "mission_01", col_type: 3 },
    StaticCol { name: "mission_02", col_type: 3 },
    StaticCol { name: "mission_03", col_type: 3 },
    StaticCol { name: "mission_04", col_type: 3 },
    StaticCol { name: "mission_05", col_type: 3 },
    StaticCol { name: "mission_06", col_type: 3 },
    StaticCol { name: "mission_07", col_type: 3 },
    StaticCol { name: "mission_08", col_type: 3 },
    StaticCol { name: "mission_09", col_type: 3 },
    StaticCol { name: "mission_10", col_type: 3 },
    StaticCol { name: "mission_11", col_type: 3 },
    StaticCol { name: "mission_12", col_type: 3 },
    StaticCol { name: "mission_13", col_type: 3 },
    StaticCol { name: "mission_14", col_type: 3 },
    StaticCol { name: "mission_15", col_type: 3 },
    StaticCol { name: "tenant_01", col_type: 3 },
    StaticCol { name: "tenant_02", col_type: 3 },
    StaticCol { name: "tenant_03", col_type: 3 },
    StaticCol { name: "tenant_04", col_type: 3 },
    StaticCol { name: "tenant_05", col_type: 3 },
    StaticCol { name: "tenant_06", col_type: 3 },
];

static COLS_91: &[StaticCol] = &[
    StaticCol { name: "id", col_type: 3 },
    StaticCol { name: "name", col_type: 3 },
    StaticCol { name: "state", col_type: 4 },
    StaticCol { name: "reward_id_01", col_type: 4 },
    StaticCol { name: "reward_id_02", col_type: 4 },
    StaticCol { name: "start_condition", col_type: 3 },
    StaticCol { name: "start_condition_param_01", col_type: 3 },
    StaticCol { name: "start_condition_param_02", col_type: 3 },
    StaticCol { name: "success_condition", col_type: 3 },
    StaticCol { name: "success_condition_param_01", col_type: 3 },
    StaticCol { name: "success_condition_param_02", col_type: 3 },
    StaticCol { name: "failure_condition", col_type: 3 },
    StaticCol { name: "failure_condition_param_01", col_type: 3 },
    StaticCol { name: "failure_condition_param_02", col_type: 3 },
    StaticCol { name: "start_flag", col_type: 9 },
    StaticCol { name: "success_flag", col_type: 9 },
    StaticCol { name: "failure_flag", col_type: 9 },
    StaticCol { name: "goal_value", col_type: 3 },
];

static COLS_92: &[StaticCol] = &[
    StaticCol { name: "id", col_type: 3 },
    StaticCol { name: "name", col_type: 4 },
    StaticCol { name: "state", col_type: 4 },
    StaticCol { name: "reward_id_01", col_type: 4 },
    StaticCol { name: "reward_id_02", col_type: 4 },
    StaticCol { name: "start_condition", col_type: 4 },
    StaticCol { name: "start_condition_param_01", col_type: 4 },
    StaticCol { name: "start_condition_param_02", col_type: 4 },
    StaticCol { name: "success_condition", col_type: 4 },
    StaticCol { name: "success_condition_param_01", col_type: 4 },
    StaticCol { name: "success_condition_param_02", col_type: 4 },
    StaticCol { name: "failure_condition", col_type: 4 },
    StaticCol { name: "failure_condition_param_01", col_type: 4 },
    StaticCol { name: "failure_condition_param_02", col_type: 4 },
    StaticCol { name: "start_flag", col_type: 9 },
    StaticCol { name: "success_flag", col_type: 9 },
    StaticCol { name: "failure_flag", col_type: 9 },
    StaticCol { name: "goal_value", col_type: 4 },
    StaticCol { name: "exp", col_type: 4 },
];

static COLS_93: &[StaticCol] = &[
    StaticCol { name: "id", col_type: 4 },
    StaticCol { name: "name", col_type: 4 },
    StaticCol { name: "tenant", col_type: 4 },
    StaticCol { name: "title", col_type: 4 },
    StaticCol { name: "age", col_type: 4 },
    StaticCol { name: "sex", col_type: 4 },
    StaticCol { name: "text", col_type: 4 },
    StaticCol { name: "level", col_type: 4 },
    StaticCol { name: "accounting", col_type: 4 },
    StaticCol { name: "service", col_type: 4 },
    StaticCol { name: "popularity", col_type: 4 },
    StaticCol { name: "strength", col_type: 4 },
    StaticCol { name: "shop", col_type: 4 },
    StaticCol { name: "food", col_type: 4 },
    StaticCol { name: "play", col_type: 4 },
    StaticCol { name: "adult", col_type: 4 },
    StaticCol { name: "sport", col_type: 4 },
    StaticCol { name: "skill", col_type: 4 },
    StaticCol { name: "fixed_skill_00", col_type: 4 },
    StaticCol { name: "fixed_skill_01", col_type: 4 },
    StaticCol { name: "flexible_skill", col_type: 4 },
    StaticCol { name: "workmate_flag", col_type: 9 },
    StaticCol { name: "appearance_condition", col_type: 4 },
    StaticCol { name: "appearance_condition_param_01", col_type: 4 },
    StaticCol { name: "appearance_condition_param_02", col_type: 4 },
    StaticCol { name: "max_level", col_type: 4 },
];

static COLS_94: &[StaticCol] = &[
    StaticCol { name: "m_Content", col_type: 3 },
    StaticCol { name: "m_Param1", col_type: 3 },
    StaticCol { name: "m_Param2", col_type: 3 },
];

static COLS_95: &[StaticCol] = &[
    StaticCol { name: "id", col_type: 4 },
    StaticCol { name: "name", col_type: 4 },
    StaticCol { name: "attribute_0", col_type: 4 },
    StaticCol { name: "attribute_1", col_type: 4 },
    StaticCol { name: "price", col_type: 4 },
    StaticCol { name: "accounting", col_type: 4 },
    StaticCol { name: "service", col_type: 4 },
    StaticCol { name: "popularity", col_type: 4 },
    StaticCol { name: "strength", col_type: 4 },
    StaticCol { name: "use_exp", col_type: 4 },
    StaticCol { name: "level", col_type: 4 },
    StaticCol { name: "growth_exp", col_type: 4 },
    StaticCol { name: "growth_sales", col_type: 4 },
    StaticCol { name: "equip_cost", col_type: 4 },
    StaticCol { name: "equip_sales", col_type: 4 },
];

static COLS_96: &[StaticCol] = &[
    StaticCol { name: "skill", col_type: 3 },
    StaticCol { name: "name", col_type: 3 },
    StaticCol { name: "text", col_type: 3 },
    StaticCol { name: "shoptype", col_type: 3 },
    StaticCol { name: "cost", col_type: 3 },
];

static COLS_97: &[StaticCol] = &[
    StaticCol { name: "id", col_type: 3 },
    StaticCol { name: "name", col_type: 3 },
    StaticCol { name: "parent_area", col_type: 4 },
    StaticCol { name: "shoptype", col_type: 4 },
    StaticCol { name: "change_type", col_type: 4 },
    StaticCol { name: "staff", col_type: 4 },
    StaticCol { name: "first_sales", col_type: 3 },
    StaticCol { name: "price", col_type: 3 },
    StaticCol { name: "appearance", col_type: 4 },
    StaticCol { name: "appearance_param_01", col_type: 4 },
    StaticCol { name: "appearance_param_02", col_type: 4 },
    StaticCol { name: "buy_01", col_type: 4 },
    StaticCol { name: "buy_01_param_01", col_type: 4 },
    StaticCol { name: "buy_01_param_02", col_type: 4 },
    StaticCol { name: "buy_02", col_type: 4 },
    StaticCol { name: "buy_02_param_01", col_type: 4 },
    StaticCol { name: "buy_02_param_02", col_type: 4 },
    StaticCol { name: "buy_03", col_type: 4 },
    StaticCol { name: "buy_03_param_01", col_type: 4 },
    StaticCol { name: "buy_03_param_02", col_type: 4 },
    StaticCol { name: "buy_scenario_flag", col_type: 9 },
    StaticCol { name: "mission_00", col_type: 4 },
    StaticCol { name: "mission_01", col_type: 4 },
    StaticCol { name: "mission_02", col_type: 4 },
    StaticCol { name: "mission_03", col_type: 4 },
    StaticCol { name: "mission_04", col_type: 4 },
    StaticCol { name: "mission_05", col_type: 4 },
];

static COLS_98: &[StaticCol] = &[
    StaticCol { name: "NAME", col_type: 1 },
    StaticCol { name: "EXPLANATION", col_type: 1 },
    StaticCol { name: "DISP_CONDITION", col_type: 7 },
    StaticCol { name: "CLEAR_CONDITION", col_type: 7 },
    StaticCol { name: "REWARD", col_type: 1 },
    StaticCol { name: "CONDITION1", col_type: 1 },
    StaticCol { name: "CONDITION2", col_type: 0 },
    StaticCol { name: "PICTURE", col_type: 1 },
    StaticCol { name: "NAME_2", col_type: 0 },
];

static COLS_99: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 2 },
    StaticCol { name: "SEQUENCE_ID", col_type: 0 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "WEATHER", col_type: 2 },
    StaticCol { name: "DRIVE_MISSION", col_type: 2 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "PRELOAD_ID", col_type: 0 },
];

static COLS_100: &[StaticCol] = &[
    StaticCol { name: "SHOP_ID", col_type: 1 },
    StaticCol { name: "MENU_UID", col_type: 0 },
    StaticCol { name: "TRIGGER_FLAG", col_type: 7 },
    StaticCol { name: "DISCOVERY_FLAG", col_type: 7 },
    StaticCol { name: "DECIDE", col_type: 1 },
    StaticCol { name: "NAME", col_type: 1 },
    StaticCol { name: "MSG_P0", col_type: 0 },
    StaticCol { name: "MSG_P1", col_type: 0 },
    StaticCol { name: "FOVY", col_type: 4 },
    StaticCol { name: "CAMERA_X", col_type: 4 },
    StaticCol { name: "CAMERA_Y", col_type: 4 },
    StaticCol { name: "CAMERA_Z", col_type: 4 },
    StaticCol { name: "CAMERA_ROTY", col_type: 4 },
    StaticCol { name: "LIMIT_L", col_type: 5 },
    StaticCol { name: "LIMIT_R", col_type: 5 },
];

static COLS_101: &[StaticCol] = &[
    StaticCol { name: "SKILL", col_type: 0 },
    StaticCol { name: "EXP_", col_type: 9 },
    StaticCol { name: "HP_ADD_VALUE", col_type: 10 },
    StaticCol { name: "HEAT_ADD_VALUE", col_type: 10 },
    StaticCol { name: "HP_APPEND_VALUE", col_type: 10 },
    StaticCol { name: "DAMAGE_APPEND_VALUE", col_type: 10 },
    StaticCol { name: "HEAT_APPEND_VALUE", col_type: 10 },
    StaticCol { name: "HEAT_DAMAGE_VALUE", col_type: 10 },
];

static COLS_102: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 0 },
    StaticCol { name: "SEQUENCE_ID", col_type: 0 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 0 },
    StaticCol { name: "MODEL_NAME", col_type: 0 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 0 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 0 },
    StaticCol { name: "DRIVE_MISSION", col_type: 0 },
    StaticCol { name: "GAME_MODE", col_type: 0 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 0 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 0 },
    StaticCol { name: "SELECT_COUNTER", col_type: 0 },
    StaticCol { name: "SOCIAL_FEEDBACK_PRESET_ID", col_type: 0 },
];

static COLS_103: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 1 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 0 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 2 },
    StaticCol { name: "RANGE_UID", col_type: 2 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "IS_VITA", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "BGM_ID0", col_type: 1 },
    StaticCol { name: "BGM_ID1", col_type: 1 },
    StaticCol { name: "BGM_ID2", col_type: 2 },
    StaticCol { name: "USEN_ID", col_type: 1 },
    StaticCol { name: "BGM_ACB_ID0", col_type: 13 },
    StaticCol { name: "PLAY_RANDOM", col_type: 1 },
    StaticCol { name: "BATTLE_STYLE", col_type: 2 },
];

static COLS_104: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 2 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "USE_DRAMA_SCANNER", col_type: 0 },
];

static COLS_105: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 1 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 2 },
    StaticCol { name: "RANGE_UID", col_type: 0 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "POKECIR_SLOW_EFFECT", col_type: 2 },
    StaticCol { name: "VOLUME_PRESET_ID", col_type: 1 },
    StaticCol { name: "VOLUME_PRESET_MUL_ID", col_type: 2 },
    StaticCol { name: "VOLUME_PRESET_ADD_ID", col_type: 2 },
];

static COLS_106: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 1 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 2 },
    StaticCol { name: "RANGE_UID", col_type: 0 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "POKECIR_SLOW_EFFECT", col_type: 2 },
    StaticCol { name: "VOLUME_PRESET_ID", col_type: 1 },
    StaticCol { name: "VOLUME_PRESET_MUL_ID", col_type: 2 },
    StaticCol { name: "VOLUME_PRESET_ADD_ID", col_type: 2 },
];

static COLS_107: &[StaticCol] = &[
    StaticCol { name: "KEY", col_type: 0 },
    StaticCol { name: "VALUE", col_type: 1 },
    StaticCol { name: "", col_type: 12 },
];

static COLS_108: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 2 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 2 },
    StaticCol { name: "RANGE_UID", col_type: 2 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "POKECIR_SLOW_EFFECT", col_type: 2 },
    StaticCol { name: "VOLUME_PRESET_ID", col_type: 1 },
    StaticCol { name: "VOLUME_PRESET_MUL_ID", col_type: 2 },
    StaticCol { name: "VOLUME_PRESET_ADD_ID", col_type: 2 },
    StaticCol { name: "REVERB_SNAPSHOT", col_type: 1 },
];

static COLS_109: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 1 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 2 },
    StaticCol { name: "DRIVE_MISSION", col_type: 2 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "SE_PORT_SET_ID", col_type: 1 },
];

static COLS_110: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 2 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 1 },
    StaticCol { name: "MODEL_NAME", col_type: 0 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 2 },
    StaticCol { name: "DRIVE_MISSION", col_type: 2 },
    StaticCol { name: "GAME_MODE", col_type: 2 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "VOICE_KIND", col_type: 1 },
];

static COLS_111: &[StaticCol] = &[
    StaticCol { name: "MISSION", col_type: 1 },
    StaticCol { name: "SEQUENCE_ID", col_type: 2 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "PLAYER", col_type: 2 },
    StaticCol { name: "MODEL_NAME", col_type: 2 },
    StaticCol { name: "STAGEID", col_type: 8 },
    StaticCol { name: "DAYNIGHT", col_type: 2 },
    StaticCol { name: "ENCOUNT_TYPE", col_type: 2 },
    StaticCol { name: "RANGE_UID", col_type: 2 },
    StaticCol { name: "GAME_MODE", col_type: 1 },
    StaticCol { name: "KAIWABGM_PLAYING", col_type: 2 },
    StaticCol { name: "DRIVE_CAMERA_IN_ROOM", col_type: 2 },
    StaticCol { name: "SELECT_COUNTER", col_type: 2 },
    StaticCol { name: "SPEAKING", col_type: 2 },
    StaticCol { name: "POKECIR_SLOW_EFFECT", col_type: 2 },
    StaticCol { name: "VOLUME_PRESET_ID", col_type: 1 },
    StaticCol { name: "VOLUME_PRESET_MUL_ID", col_type: 1 },
    StaticCol { name: "VOLUME_PRESET_ADD_ID", col_type: 2 },
];

static COLS_112: &[StaticCol] = &[
    StaticCol { name: "CATEGORY", col_type: 2 },
    StaticCol { name: "CATEGORY_EXPLANATION", col_type: 2 },
    StaticCol { name: "TIPS_NAME", col_type: 1 },
    StaticCol { name: "SCENARIO_STATUS", col_type: 7 },
    StaticCol { name: "SCENARIO_STATUS_OFF", col_type: 7 },
    StaticCol { name: "TIPS_EXPLANATION", col_type: 0 },
    StaticCol { name: "TIPS_TEX_NAME", col_type: 2 },
    StaticCol { name: "ENUM", col_type: 0 },
    StaticCol { name: "SAVE_INDEX", col_type: 10 },
    StaticCol { name: "DISP_INDEX", col_type: 10 },
    StaticCol { name: "START_CONDITION", col_type: 7 },
    StaticCol { name: "END_SCENARIO_STATE", col_type: 9 },
    StaticCol { name: "DISP_CENTER", col_type: 1 },
    StaticCol { name: "MISSION_TYPE", col_type: 1 },
    StaticCol { name: "TYPE", col_type: 1 },
    StaticCol { name: "PLAYER", col_type: 1 },
    StaticCol { name: "PRIORITY", col_type: 1 },
    StaticCol { name: "RIGHT_BOTTOM_DISP", col_type: 1 },
    StaticCol { name: "DISP_TIME", col_type: 1 },
    StaticCol { name: "DISP_TIME_2", col_type: 1 },
    StaticCol { name: "RETRY", col_type: 1 },
    StaticCol { name: "FIRST_IGNORE", col_type: 1 },
    StaticCol { name: "TIPS_SE", col_type: 10 },
    StaticCol { name: "PADV_INIT", col_type: 10 },
];

static COLS_113: &[StaticCol] = &[
    StaticCol { name: "MACHINE_ID", col_type: 2 },
    StaticCol { name: "PRICE", col_type: 2 },
    StaticCol { name: "ITEM", col_type: 11 },
    StaticCol { name: "RATIO", col_type: 1 },
    StaticCol { name: "OPEN", col_type: 7 },
    StaticCol { name: "", col_type: 1 },
];

static COLS_114: &[StaticCol] = &[
    StaticCol { name: "level", col_type: 3 },
    StaticCol { name: "sword_kiryu", col_type: 3 },
    StaticCol { name: "sword_kiryu_soul", col_type: 4 },
    StaticCol { name: "gun_kiryu", col_type: 3 },
    StaticCol { name: "gun_kiryu_soul", col_type: 4 },
    StaticCol { name: "sword_and_gun_kiryu", col_type: 3 },
    StaticCol { name: "sword_and_gun_kiryu_soul", col_type: 4 },
    StaticCol { name: "sude_kiryu", col_type: 3 },
    StaticCol { name: "sude_kiryu_soul", col_type: 4 },
];

pub static RGG_CATALOG: &[StaticTable] = &[
    StaticTable { par_name: "pause.par", file_name: "caba_profile.bin_c", num_cols: 14, num_rows: 30, cols: COLS_0 },
    StaticTable { par_name: "pause.par", file_name: "complete_heat.bin_c", num_cols: 4, num_rows: 110, cols: COLS_1 },
    StaticTable { par_name: "pause.par", file_name: "complete_minigame.bin_c", num_cols: 3, num_rows: 192, cols: COLS_2 },
    StaticTable { par_name: "pause.par", file_name: "complete_select.bin_c", num_cols: 2, num_rows: 18, cols: COLS_3 },
    StaticTable { par_name: "pause.par", file_name: "complete_tougijyo.bin_c", num_cols: 4, num_rows: 5, cols: COLS_4 },
    StaticTable { par_name: "pause.par", file_name: "extra.bin_c", num_cols: 12, num_rows: 12, cols: COLS_5 },
    StaticTable { par_name: "pause.par", file_name: "tougijyo_mode.bin_c", num_cols: 28, num_rows: 13, cols: COLS_6 },
    StaticTable { par_name: "pause.par", file_name: "tougijyo_mujin_touen_item.bin_c", num_cols: 5, num_rows: 30, cols: COLS_7 },
    StaticTable { par_name: "pause.par", file_name: "tougijyo_participant.bin_c", num_cols: 29, num_rows: 37, cols: COLS_8 },
    StaticTable { par_name: "pause.par", file_name: "tougijyo_string.bin_c", num_cols: 2, num_rows: 46, cols: COLS_9 },
    StaticTable { par_name: "pause.par", file_name: "tougijyo_tag.bin_c", num_cols: 6, num_rows: 16, cols: COLS_10 },
    StaticTable { par_name: "stay.par", file_name: "activity_list.bin_c", num_cols: 15, num_rows: 374, cols: COLS_11 },
    StaticTable { par_name: "stay.par", file_name: "battingkamuro.bin_c", num_cols: 13, num_rows: 102, cols: COLS_12 },
    StaticTable { par_name: "stay.par", file_name: "battingkamuropannel.bin_c", num_cols: 6, num_rows: 400, cols: COLS_13 },
    StaticTable { par_name: "stay.par", file_name: "battingkamuropic.bin_c", num_cols: 14, num_rows: 9, cols: COLS_14 },
    StaticTable { par_name: "stay.par", file_name: "battingkamuropinup.bin_c", num_cols: 10, num_rows: 9, cols: COLS_15 },
    StaticTable { par_name: "stay.par", file_name: "battingkamuropresent.bin_c", num_cols: 14, num_rows: 8, cols: COLS_16 },
    StaticTable { par_name: "stay.par", file_name: "battle_result.bin_c", num_cols: 4, num_rows: 30, cols: COLS_17 },
    StaticTable { par_name: "stay.par", file_name: "caba_cast_info.bin_c", num_cols: 30, num_rows: 30, cols: COLS_18 },
    StaticTable { par_name: "stay.par", file_name: "cabaret_island_area.bin_c", num_cols: 25, num_rows: 5, cols: COLS_19 },
    StaticTable { par_name: "stay.par", file_name: "cabaret_island_shop.bin_c", num_cols: 5, num_rows: 50, cols: COLS_20 },
    StaticTable { par_name: "stay.par", file_name: "colosseum_participant.bin_c", num_cols: 13, num_rows: 38, cols: COLS_21 },
    StaticTable { par_name: "stay.par", file_name: "controller_explain.bin_c", num_cols: 18, num_rows: 33, cols: COLS_22 },
    StaticTable { par_name: "stay.par", file_name: "correlation_person.bin_c", num_cols: 6, num_rows: 86, cols: COLS_23 },
    StaticTable { par_name: "stay.par", file_name: "darts_customize.bin_c", num_cols: 7, num_rows: 4, cols: COLS_24 },
    StaticTable { par_name: "stay.par", file_name: "detail_explanation.bin_c", num_cols: 6, num_rows: 1, cols: COLS_25 },
    StaticTable { par_name: "stay.par", file_name: "kyoukei_bird_param.bin_c", num_cols: 30, num_rows: 30, cols: COLS_26 },
    StaticTable { par_name: "stay.par", file_name: "money_island_area.bin_c", num_cols: 31, num_rows: 5, cols: COLS_27 },
    StaticTable { par_name: "stay.par", file_name: "money_island_shop.bin_c", num_cols: 28, num_rows: 50, cols: COLS_28 },
    StaticTable { par_name: "stay.par", file_name: "money_island_tarent.bin_c", num_cols: 15, num_rows: 30, cols: COLS_29 },
    StaticTable { par_name: "stay.par", file_name: "response_arena.bin_c", num_cols: 6, num_rows: 151, cols: COLS_30 },
    StaticTable { par_name: "stay.par", file_name: "response_chase.bin_c", num_cols: 3, num_rows: 140, cols: COLS_31 },
    StaticTable { par_name: "stay.par", file_name: "response_gaya.bin_c", num_cols: 3, num_rows: 31, cols: COLS_32 },
    StaticTable { par_name: "stay.par", file_name: "response_pokecir_live.bin_c", num_cols: 10, num_rows: 133, cols: COLS_33 },
    StaticTable { par_name: "stay.par", file_name: "response_pokecir_racer.bin_c", num_cols: 6, num_rows: 13, cols: COLS_34 },
    StaticTable { par_name: "stay.par", file_name: "response_roulette.bin_c", num_cols: 4, num_rows: 68, cols: COLS_35 },
    StaticTable { par_name: "stay.par", file_name: "response_wanderer.bin_c", num_cols: 9, num_rows: 2591, cols: COLS_36 },
    StaticTable { par_name: "stay.par", file_name: "roulette_npc.bin_c", num_cols: 18, num_rows: 11, cols: COLS_37 },
    StaticTable { par_name: "stay.par", file_name: "scenario_enemy_level.bin_c", num_cols: 14, num_rows: 22, cols: COLS_38 },
    StaticTable { par_name: "stay.par", file_name: "search_arms_agent.bin_c", num_cols: 34, num_rows: 52, cols: COLS_39 },
    StaticTable { par_name: "stay.par", file_name: "search_arms_flag_control.bin_c", num_cols: 2, num_rows: 9, cols: COLS_40 },
    StaticTable { par_name: "stay.par", file_name: "search_arms_kind.bin_c", num_cols: 3, num_rows: 297, cols: COLS_41 },
    StaticTable { par_name: "stay.par", file_name: "search_arms_location.bin_c", num_cols: 38, num_rows: 58, cols: COLS_42 },
    StaticTable { par_name: "stay.par", file_name: "search_arms_result_picture.bin_c", num_cols: 4, num_rows: 17, cols: COLS_43 },
    StaticTable { par_name: "stay.par", file_name: "tenkei_blog.bin_c", num_cols: 8, num_rows: 5, cols: COLS_44 },
    StaticTable { par_name: "stay.par", file_name: "tougijyo_enemy_set.bin_c", num_cols: 4, num_rows: 11, cols: COLS_45 },
    StaticTable { par_name: "stay.par", file_name: "tougijyo_realtime_quest.bin_c", num_cols: 4, num_rows: 8, cols: COLS_46 },
    StaticTable { par_name: "stay.par", file_name: "tougijyo_regulation_set.bin_c", num_cols: 9, num_rows: 100, cols: COLS_47 },
    StaticTable { par_name: "stay.par", file_name: "tutorial.bin_c", num_cols: 21, num_rows: 57, cols: COLS_48 },
    StaticTable { par_name: "stay.par", file_name: "ultimate.bin_c", num_cols: 12, num_rows: 32, cols: COLS_49 },
    StaticTable { par_name: "stay.par", file_name: "virtue_shop.bin_c", num_cols: 9, num_rows: 59, cols: COLS_50 },
    StaticTable { par_name: "stay.par", file_name: "walkman.bin_c", num_cols: 5, num_rows: 22, cols: COLS_51 },
    StaticTable { par_name: "boot.par", file_name: "ability.bin_c", num_cols: 27, num_rows: 581, cols: COLS_52 },
    StaticTable { par_name: "boot.par", file_name: "ability_status_table.bin_c", num_cols: 6, num_rows: 198, cols: COLS_53 },
    StaticTable { par_name: "boot.par", file_name: "action_set_sound.bin_c", num_cols: 2, num_rows: 1, cols: COLS_54 },
    StaticTable { par_name: "boot.par", file_name: "ajito.bin_c", num_cols: 13, num_rows: 1, cols: COLS_55 },
    StaticTable { par_name: "boot.par", file_name: "battle_coefficient.bin_c", num_cols: 3, num_rows: 2, cols: COLS_56 },
    StaticTable { par_name: "boot.par", file_name: "battle_deck_list.bin_c", num_cols: 11, num_rows: 39, cols: COLS_57 },
    StaticTable { par_name: "boot.par", file_name: "battle_hact_style_ratio.bin_c", num_cols: 6, num_rows: 9, cols: COLS_58 },
    StaticTable { par_name: "boot.par", file_name: "battle_param.bin_c", num_cols: 3, num_rows: 104, cols: COLS_59 },
    StaticTable { par_name: "boot.par", file_name: "battle_type.bin_c", num_cols: 14, num_rows: 1, cols: COLS_60 },
    StaticTable { par_name: "boot.par", file_name: "caption.bin_c", num_cols: 9, num_rows: 184, cols: COLS_61 },
    StaticTable { par_name: "boot.par", file_name: "chase_base.bin_c", num_cols: 23, num_rows: 4, cols: COLS_62 },
    StaticTable { par_name: "boot.par", file_name: "chase_condition.bin_c", num_cols: 4, num_rows: 28, cols: COLS_63 },
    StaticTable { par_name: "boot.par", file_name: "chase_project_table.bin_c", num_cols: 3, num_rows: 6, cols: COLS_64 },
    StaticTable { par_name: "boot.par", file_name: "complete_haruka.bin_c", num_cols: 4, num_rows: 4, cols: COLS_65 },
    StaticTable { par_name: "boot.par", file_name: "complete_heat.bin_c", num_cols: 4, num_rows: 110, cols: COLS_66 },
    StaticTable { par_name: "boot.par", file_name: "complete_shisho.bin_c", num_cols: 4, num_rows: 30, cols: COLS_67 },
    StaticTable { par_name: "boot.par", file_name: "continuepoint.bin_c", num_cols: 4, num_rows: 10, cols: COLS_68 },
    StaticTable { par_name: "boot.par", file_name: "dictionary.bin_c", num_cols: 4, num_rows: 0, cols: COLS_69 },
    StaticTable { par_name: "boot.par", file_name: "dictionary_ignore.bin_c", num_cols: 1, num_rows: 0, cols: COLS_70 },
    StaticTable { par_name: "boot.par", file_name: "effect_low_list.bin", num_cols: 2, num_rows: 7, cols: COLS_71 },
    StaticTable { par_name: "boot.par", file_name: "effect_low_list.bin_c", num_cols: 2, num_rows: 7, cols: COLS_72 },
    StaticTable { par_name: "boot.par", file_name: "encount_reward.bin_c", num_cols: 4, num_rows: 66, cols: COLS_73 },
    StaticTable { par_name: "boot.par", file_name: "environment.bin_c", num_cols: 3, num_rows: 131, cols: COLS_74 },
    StaticTable { par_name: "boot.par", file_name: "exp.bin_c", num_cols: 43, num_rows: 216, cols: COLS_75 },
    StaticTable { par_name: "boot.par", file_name: "explanation_main_scenario.bin_c", num_cols: 6, num_rows: 210, cols: COLS_76 },
    StaticTable { par_name: "boot.par", file_name: "explanation_sub_story.bin_c", num_cols: 10, num_rows: 447, cols: COLS_77 },
    StaticTable { par_name: "boot.par", file_name: "game_live_streaming.bin_c", num_cols: 15, num_rows: 15, cols: COLS_78 },
    StaticTable { par_name: "boot.par", file_name: "hact_attr.bin_c", num_cols: 2, num_rows: 46, cols: COLS_79 },
    StaticTable { par_name: "boot.par", file_name: "haruka_gauge.bin_c", num_cols: 2, num_rows: 6, cols: COLS_80 },
    StaticTable { par_name: "boot.par", file_name: "human_model.bin_c", num_cols: 10, num_rows: 146, cols: COLS_81 },
    StaticTable { par_name: "boot.par", file_name: "item.bin_c", num_cols: 53, num_rows: 963, cols: COLS_82 },
    StaticTable { par_name: "boot.par", file_name: "item_alias.bin_c", num_cols: 3, num_rows: 664, cols: COLS_83 },
    StaticTable { par_name: "boot.par", file_name: "item_mark.bin_c", num_cols: 6, num_rows: 95, cols: COLS_84 },
    StaticTable { par_name: "boot.par", file_name: "item_weapon_parameter.bin_c", num_cols: 9, num_rows: 184, cols: COLS_85 },
    StaticTable { par_name: "boot.par", file_name: "kiyaku.bin_c", num_cols: 2, num_rows: 2, cols: COLS_86 },
    StaticTable { par_name: "boot.par", file_name: "money_result.bin_c", num_cols: 6, num_rows: 89, cols: COLS_87 },
    StaticTable { par_name: "boot.par", file_name: "motion_generate.bin_c", num_cols: 2, num_rows: 219, cols: COLS_88 },
    StaticTable { par_name: "boot.par", file_name: "motion_hand_pattern.bin_c", num_cols: 1, num_rows: 18, cols: COLS_89 },
    StaticTable { par_name: "boot.par", file_name: "nawabari_area.bin_c", num_cols: 25, num_rows: 7, cols: COLS_90 },
    StaticTable { par_name: "boot.par", file_name: "nawabari_mission_area.bin_c", num_cols: 18, num_rows: 105, cols: COLS_91 },
    StaticTable { par_name: "boot.par", file_name: "nawabari_mission_tenant.bin_c", num_cols: 19, num_rows: 252, cols: COLS_92 },
    StaticTable { par_name: "boot.par", file_name: "nawabari_npc.bin_c", num_cols: 26, num_rows: 640, cols: COLS_93 },
    StaticTable { par_name: "boot.par", file_name: "nawabari_reward.bin_c", num_cols: 3, num_rows: 5, cols: COLS_94 },
    StaticTable { par_name: "boot.par", file_name: "nawabari_shop_type.bin_c", num_cols: 15, num_rows: 320, cols: COLS_95 },
    StaticTable { par_name: "boot.par", file_name: "nawabari_skill.bin_c", num_cols: 5, num_rows: 7, cols: COLS_96 },
    StaticTable { par_name: "boot.par", file_name: "nawabari_tenant.bin_c", num_cols: 27, num_rows: 42, cols: COLS_97 },
    StaticTable { par_name: "boot.par", file_name: "otazunemono.bin_c", num_cols: 9, num_rows: 17, cols: COLS_98 },
    StaticTable { par_name: "boot.par", file_name: "reactor_preload.bin_c", num_cols: 14, num_rows: 2, cols: COLS_99 },
    StaticTable { par_name: "boot.par", file_name: "restaurant_menu.bin_c", num_cols: 15, num_rows: 5, cols: COLS_100 },
    StaticTable { par_name: "boot.par", file_name: "skill_status_table.bin_c", num_cols: 8, num_rows: 134, cols: COLS_101 },
    StaticTable { par_name: "boot.par", file_name: "social_feedback_preset.bin_c", num_cols: 14, num_rows: 0, cols: COLS_102 },
    StaticTable { par_name: "boot.par", file_name: "sound_bgm.bin_c", num_cols: 21, num_rows: 185, cols: COLS_103 },
    StaticTable { par_name: "boot.par", file_name: "sound_drama_scanner.bin_c", num_cols: 4, num_rows: 1, cols: COLS_104 },
    StaticTable { par_name: "boot.par", file_name: "sound_hpf_preset.bin_c", num_cols: 17, num_rows: 63, cols: COLS_105 },
    StaticTable { par_name: "boot.par", file_name: "sound_lpf_preset.bin_c", num_cols: 17, num_rows: 30, cols: COLS_106 },
    StaticTable { par_name: "boot.par", file_name: "sound_profile.bin_c", num_cols: 3, num_rows: 25, cols: COLS_107 },
    StaticTable { par_name: "boot.par", file_name: "sound_reverb_preset.bin_c", num_cols: 18, num_rows: 46, cols: COLS_108 },
    StaticTable { par_name: "boot.par", file_name: "sound_se_port_set.bin_c", num_cols: 14, num_rows: 86, cols: COLS_109 },
    StaticTable { par_name: "boot.par", file_name: "sound_step.bin_c", num_cols: 14, num_rows: 8, cols: COLS_110 },
    StaticTable { par_name: "boot.par", file_name: "sound_volume_preset.bin_c", num_cols: 18, num_rows: 109, cols: COLS_111 },
    StaticTable { par_name: "boot.par", file_name: "tips_tutorial.bin_c", num_cols: 24, num_rows: 180, cols: COLS_112 },
    StaticTable { par_name: "boot.par", file_name: "vending_machine.bin_c", num_cols: 6, num_rows: 139, cols: COLS_113 },
    StaticTable { par_name: "boot.par", file_name: "weapon_status_table.bin_c", num_cols: 9, num_rows: 50, cols: COLS_114 },
];

pub fn find_candidates_in_catalog(target_col: usize, min_rows: usize) -> Vec<StaticTable> {
    RGG_CATALOG.iter()
        .filter(|t| t.num_cols > target_col && t.num_rows >= min_rows)
        .copied()
        .collect()
}
