import subprocess,os,struct,glob,tempfile
import shutil

import config
gamename = config.gamename
sox = "sox"

if not shutil.which("sox"):
    raise Exception("sox command not in path, please install it")
# BTW convert wav to mp3: ffmpeg -i input.wav -codec:a libmp3lame -b:a 330k output.mp3

#wav_files = glob.glob("sounds/*.wav")

this_dir = os.path.dirname(__file__)
sound_dir = os.path.join(this_dir,"..","sounds")

this_dir = os.path.dirname(__file__)
src_dir = os.path.join(this_dir,"../../src/amiga")
outfile = os.path.join(src_dir,"sounds.68k")
sndfile = os.path.join(src_dir,"sound_entries.68k")

hq_sample_rate = 18004
vhq_sample_rate = 22030

EMPTY_SND = "EMPTY_SND"
sound_dict = {


"BOSS_KILLED_SND"               :{"index":0,"channel":2,"sample_rate":hq_sample_rate,"priority":1},
"BEE_KILLED_SND"               :{"index":1,"channel":3,"sample_rate":hq_sample_rate,"priority":1},
"MOTH_KILLED_SND"               :{"index":2,"channel":2,"sample_rate":hq_sample_rate,"priority":1},
"GALAXIAN_KILLED_SND"        :{"index":3,"channel":2,"sample_rate":hq_sample_rate,"priority":1},
"CAPTURE_DOWN_SND"               :{"index":5,"pattern":19,"volume":12,'loops':True},
"CAPTURE_UP_SND"               :{"index":0x17,"pattern":20,"volume":12,'loops':True},
"SHOT_SND"               :{"index":0xF,"channel":1,"sample_rate":hq_sample_rate,"priority":10},
"CHALLENGING_STAGE_SND"    :{"index":0xD,"channel":0,"sample_rate":hq_sample_rate},
"MUTANT_SND"               :{"index":0x12,"channel":2,"sample_rate":hq_sample_rate},
"ATTACK_SND"               :{"index":0x13,"channel":3,"sample_rate":hq_sample_rate},
"TICK_SND"               :{"index":0x15,"channel":2,"sample_rate":hq_sample_rate,"priority":1},
"EXPLOSION_SND"            :{"index":0x19,"channel":0,"sample_rate":hq_sample_rate},
"CREDIT_SND"               :{"index":0X1A,"channel":0,"sample_rate":hq_sample_rate},
"EXTRA_LIFE_SND"       :{"index":0x1B,"channel":3,"sample_rate":hq_sample_rate,"priority":20},

"GAME_START_SND"       :{"index":0x9,"pattern":0,"volume":24,"ticks":340,'loops':False},
"HIGH_SCORE_SND"       :{"index":0x10,"pattern":2,"volume":24,'loops':True},
"HIGHEST_SCORE_SND"       :{"index":0xC,"pattern":4,"volume":24,'loops':True},
"END_CHALLENGE_SND"       :{"index":0xE,"pattern":12,"volume":24,"ticks":360,'loops':False},
"PERFECT_SND"         :{"index":0x14,"pattern":14,"volume":36,'loops':False,"ticks":240},
"FIGHTER_CAPTURED_SND"    :{"index":0x16,"pattern":16,"volume":24,'loops':False,"ticks":280},
"FIGHTER_KILLED_SND"    :{"index":6,"pattern":17,"volume":24,'loops':False,"ticks":130},
"FIGHTER_RESCUED_SND"    :{"index":0x18,"pattern":18,"volume":24,'loops':False,"ticks":280},

}

max_sound = 0x20  # max(x["index"] for x in sound_dict.values())+1
sound_table = [""]*max_sound
sound_table_set_1 = ["\t.long\t0,0"]*max_sound




snd_header = rf"""
# sound tables
#
# the "sound_table" table has 8 bytes per entry
# first word: 0: no entry, 1: sample, 2: pattern from music module
# second word: 0 except for music module: pattern number
# longword: sample data pointer if sample, 0 if no entry and
# 2 words: 0/1 noloop/loop followed by duration in ticks
#
FXFREQBASE = 3579564

    .macro    SOUND_ENTRY    sound_name,size,channel,soundfreq,volume,priority
\sound_name\()_sound:
    .long    \sound_name\()_raw
    .word   \size
    .word   FXFREQBASE/\soundfreq,\volume
    .byte    \channel
    .byte    \priority
    .endm

"""

def write_asm(contents,fw):
    n=0
    for c in contents:
        if n%16 == 0:
            fw.write("\n\t.byte\t0x{:x}".format(c))
        else:
            fw.write(",0x{:x}".format(c))
        n += 1
    fw.write("\n")

music_module_label = f"{gamename}_tunes"

raw_file = os.path.join(tempfile.gettempdir(),"out.raw")
with open(sndfile,"w") as fst,open(outfile,"w") as fw:
    fst.write(snd_header)

    fw.write("\t.section\t.datachip\n")
    fw.write("\t.global\t{}\n".format(music_module_label))

    for wav_file,details in sound_dict.items():
        wav_name = os.path.basename(wav_file).lower()[:-4]
        if details.get("channel") is not None:
            fw.write("\t.global\t{}_raw\n".format(wav_name))


    for wav_entry,details in sound_dict.items():
        sound_index = details["index"]

        channel = details.get("channel")
        if channel is None:
            # if music loops, ticks are set to 1 so sound orders only can happen once (else music is started 50 times per second!!)

            sound_table_set_1[sound_index] = "\t.word\t{},{},{}\n\t.byte\t{},{}".format(2,details["pattern"],details.get("ticks",0),details["volume"],int(details["loops"]))
        else:
            wav_name = os.path.basename(wav_entry).lower()[:-4]
            wav_file = os.path.join(sound_dir,wav_name+".wav")

            def get_sox_cmd(sr,output):
                return [sox,"--volume","1.0",wav_file,"--channels","1","--bits","8","-r",str(sr),"--encoding","signed-integer",output]


            used_sampling_rate = details["sample_rate"]
            used_priority = details.get("priority",1)

            cmd = get_sox_cmd(used_sampling_rate,raw_file)

            subprocess.check_call(cmd)
            with open(raw_file,"rb") as f:
                contents = f.read()

            # compute max amplitude so we can feed the sound chip with an amped sound sample
            # and reduce the replay volume. this gives better sound quality than replaying at max volume
            # (thanks no9 for the tip!)
            signed_data = [x if x < 128 else x-256 for x in contents]
            maxsigned = max(signed_data)
            minsigned = min(signed_data)

            amp_ratio = max(maxsigned,abs(minsigned))/128

            wav = os.path.splitext(wav_name)[0]
            sound_table[sound_index] = "    SOUND_ENTRY {},{},{},{},{},{}\n".format(wav,len(signed_data)//2,channel,used_sampling_rate,int(64*amp_ratio),used_priority)
            sound_table_set_1[sound_index] = f"\t.word\t1,{int(details.get('loops',0))}\n\t.long\t{wav}_sound"

            if amp_ratio > 0:
                maxed_contents = [int(x/amp_ratio) for x in signed_data]
            else:
                maxed_contents = signed_data

            signed_contents = bytes([x if x >= 0 else 256+x for x in maxed_contents])
            # pre-pad with 0W, used by ptplayer for idling
            if signed_contents[0] != b'\x00' and signed_contents[1] != b'\x00':
                # add zeroes
                signed_contents = struct.pack(">H",0) + signed_contents

            contents = signed_contents
            # align on 16-bit
            if len(contents)%2:
                contents += b'\x00'
            # pre-pad with 0W, used by ptplayer for idling
            if contents[0] != b'\x00' and contents[1] != b'\x00':
                # add zeroes
                contents = b'\x00\x00' + contents

            fw.write("{}_raw:   | {} bytes".format(wav,len(contents)))

            if len(contents)>65530:
                raise Exception(f"Sound {wav_entry} is too long")
            write_asm(contents,fw)

    # make sure next section will be aligned
    with open(os.path.join(sound_dir,f"{gamename}_conv.mod"),"rb") as f:
        contents = f.read()
    fw.write("{}:".format(music_module_label))
    write_asm(contents,fw)
    fw.write("\t.align\t8\n")


    fst.writelines(sound_table)
    fst.write("\n\t.global\t{0}\n\n{0}:\n".format("sound_table"))
    for i,st in enumerate(sound_table_set_1):
        fst.write(st)
        fst.write(" | {}\n\n".format(i))




