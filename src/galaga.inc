

***    
*** BUILD OPTIONS
***

    * hardware options
    OPT_DISABLE_BG_LAYER=0
    OPT_DISABLE_SPRITES=0
   
	* cheats to test game
    * score is decimal format
	* all options must be zeroed for release
    OPT_START_SCORE=0

	OPT_START_WITH_HIGH_SCORE_TABLE=0
	OPT_SKIP_GAME_DEMO=0

	OPT_ONLY_ONE_LIFE=0

***
*** end of BUILD OPTIONS
***




* sound ordinals

    .equ  BOSS_KILLED_SND,         0x0
    .equ  BEE_KILLED_SND,     0x01
    .equ  MOTH_KILLED_SND,         0x02
    .equ  GALAXIAN_KILLED_SND,    0x03
    .equ  GREEN_BOSS_HIT_SND,     0x03
    .equ  CAPTURE_DOWN_SND,     0x05
    .equ  CAPTURE_UP_SND,     0x06
    .equ  SHOT_SND,           0xF
	.equ  CHALLENGING_STAGE_SND, 0xD
    .equ  MUTANT_SND,         0x12
    .equ  ATTACK_SND,         0x13
    .equ  TICK_SND,           0x15
    .equ  EXPLOSION_SND,         0x19
    .equ  CREDIT_SND,         0x1A
    .equ  EXTRA_LIFE_SND,         0x1B
	
    .equ  GAME_START_SND,         0x9
    
    .equ  END_CHALLENGE_SND,         0xE
    .equ  PERFECT_SND,         0x14
	.equ  SND_COUNT,  0x20
    
