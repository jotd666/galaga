|| structs.inc
||  Definitions of macros and other symbols to emulate C-style data structures.
||


| This bit of macro non-sense automatically takes care of computing the offset
| to each element using the size argument specified in bytes.
| The base of the structure is defined using a label and the '.ds' directive
| to allocate the storage e.g.
|
|  ld a, (ds_plyr_actv+_nships)
|

.macro _STRUCT
  .set _offset_,0
.endm

.macro _DS _element, _size
   \_element = _offset_
   .set _offset_,_offset_+\_size
.endm


_STRUCT  | plyr_state
  _DS  _b_nships             1   | 0x00  = mchn_cfg_nships
  _DS  _b_stgctr             1   | 0x01
  _DS  _p_atkwav_tbl         2+2   | 0x02  player's private pointer to attack wave object setup tables
  _DS  _b_nestlr_inh         1   | 0x04  1 or 0 .. flag to f_2A90, if 1 signifies nest left/right movement should stop
  _DS  _b_not_chllg_stg      1   | 0x05  stg_ctr+1%4 (1 if not challenge stage)
  _DS  _b_attkwv_ctr         1   | 0x06  atack_wave_ctr++
  _DS  _b_2ship              1   | 0x07  1 ...player is two-ship

  _DS  _b_bmbr_boss_cobj     1   | 0x08  object/index of active capturing boss
  _DS  _b_cboss_slot         1   | 0x09  offset of slot used by capture boss, referenced by cpu0:f_21CB
  _DS  _b_captr_flag         1   | 0x0A  related to ship-capture status
  _DS  _b_bmbr_boss_cflag    1   | 0x0B  1 as capturing boss initiates his dive
  _DS  _b_bmbr_boss_wingm    1   | 0x0C  bomber boss wingman-enable toggled to select boss-bomber mode i.e. capture or wingman

  _DS  _b_bbee_obj           1   | 0x0D  offset of object that spawns special bonus convoys
  _DS  _b_bbee_clr_a         1   | 0x0E  flashing color 'A' for special bonus convoys
  _DS  _b_bbee_clr_b         1   | 0x0F  flashing color 'B' for special bonus convoys

  _DS  _ds_bmbr_boss_scode   8   | 0x10  bonus code/score attributes e.g. "01B501B501B501B5"
  _DS  _unused               6-2   | 0x18-0x1D ?
  _DS  _b_mcfg_bonus         1   | 0x1E  load at game start from w_mchn_cfg_bonus_9980 ... $9980
  _DS  _b_plyr_swap_tmr      1   | 0x1F  game_tmr_2, player1/2 switch
  _DS  _b_plyr_nbr           1   | 0x20  0==plyr1, 1==plyr2
  _DS  _b_bbee_tmr           1   | 0x21  bonus bee launch timer
  _DS  _b_atk_wv_enbl        1   | 0x22  attack_wave_enable (0 when respawning player ship)
  _DS  _b_enmy_ct_actv       1   | 0x23  bugs_actv_nbr
  _DS  _w_hit_ct             2   | 0x24  game number of hits
  _DS  _w_shot_ct            2   | 0x26  game shots fired count
  _DS  _b_sndflag            1   | 0x28  enable "pulsing_sound" (_fx[0])

* offset names for ds_bug_motion_que_9100 structures
mq_fine_y_00 = 0x00
mq_y_01 = 0x01		| X on amiga
mq_fine_x_02 = 0x02
mq_x_03 = 0x03      | Y on amiga
mq_angle_lsb_04 = 0x04
mq_angle_msb_05 = 0x05
mq_home_position_y_06 = 0x06
mq_home_position_x_07 = 0x07
mq_fp_lsb_08 = 0x08
mq_fp_msb_09 = 0x09
mq_unknown_0A = 0x0A
mq_unknown_0B = 0x0B
mq_angle_increment_0C = 0x0C
mq_timeout_0d = 0x0D
mq_drop_bomb_counter_0e = 0x0E
mq_drop_bomb_enable_0f = 0x0F
mq_object_id_10 = 0x10
mq_x_offset_11 = 0x11
mq_y_offset_12 = 0x12
mq_state_13 = 0x13

* states

ST_ROTATING_BACK_TO_COLLECTIVE = 2

