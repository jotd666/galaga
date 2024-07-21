
*
* input file mrw.s
*
*
* mrw.s:
*  defines variables in "read-write" memory.
*
*  This project provides information about the design of the software
*  programming of the original Galaga arcade game, (c) 1981 NAMCO LTD.
*  All files associated with this project are an original documentation
*  work, copyright 2012 by Glenn A. Neidermeier.
*
* Permission is granted to anyone to use the information provided here for
* any non-commerial purpose with the following restrictions:
*
* 1) You are responsible for any legal issues arising from your use of this
*    information.
* 2) If any changes are made to any files in this project, they should be
*    identified as having been modified and by whom.
*
*
*  The build requires the axXXXX assembler (asez80 variant which includes
*  support for some undocumented opcodes). Code for all 3 Z80 CPUs is
*  generated from one build by making use of the bank-switching capability of
*  asXXXX. The linker also allows most of the .org directives to be
*  eliminated, and instead module placement is controlled by .area directive
*  and located at link time.
*
*  The ROM checksums are also left as commented .db directives, but are
*  actually generated completely at link time by the remarkable srec_cat tool.
*
*
*  What follows is a catch-all for any additional information...
*
*
*  Sprite hardware SFRs ... I got this information a long long time ago from
*  MAME version 21.5 or something like that which had the first Galaga driver:
*
*   SPRCODE: sprite code/color
*   8b00-8b7f buffer  8b80-8bff
*    offset[0]: tile code
*    offset[1]: color map code
*
*   SPRPOSN: sprite position
*   9300-937f buffer  9380-93ff
*    offset[0]: sx
*    offset[1]: sy<0:7>
*
*   SPRCTRL: sprite control
*   9b00-9b7f buffer  9b80-9bff
*    offset[0]
*     0: flipx - flip about the X axis, i.e. "up/down"
*     1: flipy - flip about the Y axis, i.e. "left/right"
*     2: dblh - MAME may not do dblh unless dblw is also set... (this may not be true)
*     3: dblw
*    offset[1]
*     0: sy<8>
*     1: enable
*
*     Doubling effects seem to copy/mirror the sprite image .. but not always?
*
*

*
* Tile RAM & color RAM layout.
*    Tile rows  0-1:   $8300 - 803F
*    Playfield area:   $8040 - 83BF
*    Tile rows 32-35:  $83C0 - 83FF
*
*    In Tile rows 0,1,32,35, the length is $20 bytes, but 2 bytes at each end
*    are not visible, but it simplifies the math!
*
*    2 bytes                            	|| 2 bytes (not visible)
*   ----------------------------------------------------
*   .3DF     .3DD                              .3C2  .3C0     <- Row 2
*   .3FF     .3FD                              .3E2  .3E0     <- Row 3
*            .3A0-------------------------.060 .040
*                                       	|||
*            .3BF-------------------------.07F .05F
*   .01F     .01D                              .002  .000     <- Row 0
*   .03F     .03D                              .022  .020     <- Row 1
*

*=============================================================================
*  This module implements all the memory read-write blocks, which exist in
*  a single data address space common to all 3 Z80 CPUs.
*  The approach taken is that anything here could be moved if the code were
*  ported to a different platform.
*  There is a separate file "sfrs.inc" which provides equates for the
*  addresses of speqcial function registers which are specific to the hardware.
*  It could be argued that the sprite register blocks should be
*  handled as simple equates as well.
*
*  3 separate .areas are defined here for each of the shared RAM banks located at
*  $8800, $9000, and $9800 ($0400 bytes each).
*  Those areas could be located at link time by '-b' arguments to the linker
*  but relocatable symbols and absolute symbols can't be used in expressions together.
*-----------------------------------------------------------------------------

*=============================================================================
* RAM0
* Description:
*   $0400 bytes, $8800
*-----------------------------------------------------------------------------

o_bg_videoram_8000 = 0x0000
o_bg_colorram_8400 = 0x0400

* Object status structure... 2 bytes per element (indexed same as sprite registers).
*  [ 0 + n ] : object state
*  [ 1 + n ] : byte-offset (index) into bug_motion_que[]

o_object_states_8800 = 0x0800		| $40 elements

* Space for 5 attack wave setup tables. Each table can vary in size, because
* in each wave there are a varying number of "transients" bug (have no home
* and simply fly off the screen) so each wave has slots for up to 16
* bugs. There are always 8 bugs in each wave that fly "home".
* Each player has a private pointer initialized to offset 0 of this table at
* beginning of each new stage ... actv_plyr_state[0x02]
* Since the table size can vary, the end-of-table is indicated  by $7F.

o_ds_8920 = 0x0920

* Temp vars for _top5_dlg_proc ... gg1-4
*	   .skip     0x04          | ptr to plyr1 score or plyr2 score on screen.
*       .skip     0x01       | L==2, R==8 X=A   previous controller state
*       .skip     0x01       | character selection counter/timer
*       .skip     0x04       | pointer to new name in table
*	    .skip     0x06       | unused (jotd: removed 4 bytes so rest is not shifted)
*       .skip     0x01       | lower byte of current input character's address in v-ram
*       .skip     0x01       | 1==1ST place etc.
*       .skip     0x0E       | unused

o_b_8A00 = 0x0a00

* Top5 Table scores

o_b_best5_score1_8a20 = 0x0a20
o_b_best5_score_8a20 = 0x0a20
o_b_best5_score2_8a26 = 0x0a26
o_b_best5_score3_8a2c = 0x0a2c
o_b_best5_score4_8a32 = 0x0a32
o_b_best5_score5_8a38 = 0x0a38
o_b_best5_name1_8a3e = 0x0a3e
o_b_best5_name2_8a41 = 0x0a41
o_b_best5_name3_8a44 = 0x0a44
o_b_best5_name4_8a47 = 0x0a47
o_b_best5_name5_8a4a = 0x0a4a

* origin base of sprite data block
* mrw and sfr blocks NEED to be contiguous because sometimes the game adds 0x80
* to peek in sfr registers (which have write but also read capability)

o_ds_sprite_code_8B00 = 0x0b00
o_mrw_sprite_code_8B00 = 0x0b00
o_sfr_sprite_code_8B80 = 0x0b80

o_ds_cpu0_task_actv_9000 = 0x1000
o_ds_cpu1_task_actv_9020 = 0x1020
o_ds_atk_wav_tmp_buf_9100 = 0x1100
o_ds_bug_motion_que_9100 = 0x1100
o_ds_9100 = 0x1100
o_ds_tmp_9100 = 0x1100


*-----------------------------------------------------------------------------
* The following motley collection of global variables are situated at
* odd addresses, apparently because the clever designers didn't want to
* waste the odd-bytes at 0x9200. At the end of these globals, the instruction
* counter will be rollled-back and a new label created to define the array of
* $30 bytes and allow it to be treated as a separate structure.
*-----------------------------------------------------------------------------
*-----------------------------------------------------------------------------
* Object-collision notification to f_update_enemy_status_1db3 from cpu1:c_076A (even-bytes)
*-----------------------------------------------------------------------------

o_ds_glbls_9200 = 0x1200
o_b_obj_collsn_notif_9200 = 0x1200

* 0==Game Ended   (not described in manual)
* 1==ATTRACT_MODE, 2==READY_TO_PLAY_MODE, 3==PLAY_MODE
* ?==SELF_TEST_MODE  (doesn't have a corresponding enumeration value)

o_b8_game_state_9201 = 0x1201

*       .skip     0x01       | game states (1, 2, 3, 4 from the manual)
*       .skip     0x01
**_b_9203
*       .skip     0x01       | jp table index demo mode
*       .skip     0x01
**_b_9205
*       .skip     0x01       | index for text strings, demo
*       .skip     0x01
**_b_9207
*       .skip     0x01       | counter, demo
*       .skip     0x01
**                           | state, once near beginning of round (demo or play) $81->$1
*
**_b_9209                    | demo only
**                           | 07DD(sub-1)
*       .skip     0x01
*       .skip     0x01
**_b_920B
*       .skip     0x01       | conditions for doing flying bug attack
*       .skip     0x01       | 1 at demo mode, 3 at game start (after intro),
*                            * 0 at HEROES screen, 0 when ship appear on training mode, 0 when coin-in,
**_b_920D
*       .skip     0x01
*       .skip     0x01
**_b_920F
*       .skip     0x01       | flag, bug nest movement left/right
*       .skip     0x01       | 07DD, 1DC1 in game
**_b_9211
*       .skip     0x01       | cp with (b_9A80 + 0x00) in cpu2
*       .skip     0x01
**_b_9213
*       .skip     0x01       | restart_stage "end of attack" (all attackers go home)
*       .skip     0x01       | 07DD, 1DC1
*b_flip_screen_9215:
*       .skip     0x01
*       .skip     0x01


o_b_flip_screen_9215 = 0x1215
o_p_attrmode_sptiles_9280 = 0x1280
o_b_9280 = 0x1280
o_pdb_demo_fghtrvctrs_9282 = 0x1282
o_ds2_stg_chllg_rnd_attrib_9284 = 0x1284
o_b_bugs_flying_cnt_9286 = 0x1286
o_b_bugs_flying_nbr_9287 = 0x1287
o_b_bug_flyng_hits_p_round_9288 = 0x1288
o_b_bug_que_idx_9289 = 0x1289
o_ds5_captr_status_928a = 0x128a
o_ds_bug_collsn_hit_mult_9290 = 0x1290
o_b_92A0 = 0x12a0
o_ds3_frame_cts_92A0 = 0x12a0
o_b_92B0 = 0x12b0
o_b_92C0 = 0x12c0
o_b_92E2 = 0x12e2
o_b_bugs_actv_cnt_92a6 = 0x12a6
o_b_bugs_actv_nbr_92a7 = 0x12a7
o_w_bug_flying_hit_cnt_92a8 = 0x12a8
o_ds4_game_tmrs_92ac = 0x12ac
o_bmbr_boss_pool_92ca = 0x12ca
o_b_CPU1_in_progress_92d6 = 0x12d6
o_b_CPU2_in_progress_92d7 = 0x12d7
o_pb_attk_wav_IDs_92e0 = 0x12e0
o_mrw_sprite_posn_9300 = 0x1300
o_ds_sprite_posn_9300 = 0x1300
o_sfr_sprite_posn_9380 = 0x1380
o_ds_RAM2_9800 = 0x1800
o_ds_hpos_spcoords_9800 = 0x1800
o_ds_plyr_actv_9820 = 0x1820
o_ds_plyr_data_9820 = 0x1820
o_ds_plyr_susp_9860 = 0x1860
o_ds_susp_plyr_obj_data_98b0 = 0x18b0
o_ds_cpu0_task_resrv_98e0 = 0x18e0
o_ds_hpos_loc_offs_9900 = 0x1900
o_ds_hpos_loc_orig_9900 = 0x1900
o_ds10_9920 = 0x1920
o_ds_mchn_cfg_9980 = 0x1980
o_w_mchn_cfg_bonus_9980 = 0x1980
o_b_mchn_cfg_nships_9982 = 0x1982
o_b_mchn_cfg_cab_type_9983 = 0x1983
o_b_mchn_cfg_rank_9984 = 0x1984
o_ds20_99E0 = 0x19e0
o_b16_tmp_99b0 = 0x19b0
o_ds3_X3attackcfg_99b0 = 0x19b0
o_b8_X3attackcfg_ct_99b0 = 0x19b0
o_b8_X3attackcfg_parm0_99b1 = 0x19b1
o_b8_X3attackcfg_parm1_99b2 = 0x19b2
o_b8_two_plyr_game_99b3 = 0x19b3
o_b8_bugnest_onoff_scrn_tmr_99b4 = 0x19b4
o_ds3_io_input_99b5 = 0x19b5
o_b8_credit_cnt_99b8 = 0x19b8
o_ds_star_ctrl_99b9 = 0x19b9
o_b8_ship_collsn_detectd_status_99bf = 0x19bf
o_ds_new_stage_parms_99c0 = 0x19c0
o_ds10_mchn_data_99e0 = 0x19e0
o_b16_ttl_plays_bcd_99e0 = 0x19e0
o_b32_sum_score_bcd_99e2 = 0x19e2
o_b32_gametime_secs_bcd_99e6 = 0x19e6
o_b16_bonus_ct_bcd_99ea = 0x19ea
o_b_9A00 = 0x1a00
o_b_9A30 = 0x1a30
o_b_9A60 = 0x1a60
o_b_9A70 = 0x1a70
o_b_9A80 = 0x1a80
o_ds_9AA0 = 0x1aa0
o_b_9AA0 = 0x1aa0
o_b_9AC0 = 0x1ac0
o_mrw_sprite_ctrl_9B00 = 0x1b00
o_ds_sprite_ctrl_9B00 = 0x1b00
o_sfr_sprite_ctrl_9B80 = 0x1b80
