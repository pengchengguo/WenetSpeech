# Copyright 2021  Xiaomi Corporation (Author: Yongqing Wang)
#                 Mobvoi Inc(Author: Di Wu, Binbin Zhang)

import sys
import os
import argparse
import json


def get_args():
    parser = argparse.ArgumentParser(description="""
      This script is used to process raw json dataset of WenetSpeech,
      where the long wav is splitinto segments and
      data of wenet format is generated.
      """)
    parser.add_argument('input_json', help="""Input json file of WenetSpeech""")
    parser.add_argument('output_dir', help="""Output dir for prepared data""")
    parser.add_argument('--pipe-format', action='store_true', default='False',
                        help="""If true, wav.scp is generated with pipeline format""")

    args = parser.parse_args()
    return args


def meta_analysis(input_json, output_dir, pipe):
    input_dir = os.path.dirname(input_json)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        with open(input_json, 'r') as injson:
            json_data = json.load(injson)
    except Exception:
        sys.exit(f'Failed to load input json file: {input_json}')
    else:
        if json_data['audios'] is not None:
            with open(f'{output_dir}/text', 'w') as utt2text, \
                 open(f'{output_dir}/segments', 'w') as segments, \
                 open(f'{output_dir}/utt2dur', 'w') as utt2dur, \
                 open(f'{output_dir}/wav.scp', 'w') as wavscp, \
                 open(f'{output_dir}/utt2subsets', 'w') as utt2subsets, \
                 open(f'{output_dir}/reco2dur', 'w') as reco2dur:
                for long_audio in json_data['audios']:
                    try:
                        long_audio_path = os.path.realpath(
                            os.path.join(input_dir, long_audio['path']))
                        aid = long_audio['aid']
                        segments_lists = long_audio['segments']
                        duration = long_audio['duration']
                        assert (os.path.exists(long_audio_path))
                    except AssertionError:
                        print(f'''Warning: {aid} something is wrong,
                                  maybe AssertionError, skipped''')
                        continue
                    except Exception:
                        print(f'''Warning: {aid} something is wrong, maybe the
                                  error path: {long_audio_path}, skipped''')
                        continue
                    else:
                        if pipe is True:
                            # pipe:1 means that write to memory
                            wavscp.write(f'{aid}\tffmpeg -i {long_audio_path}'
                                         ' -ar 16000 -f wav pipe:1 |\n')
                        else:
                            wavscp.write(f'{aid}\t{long_audio_path}\n')
                        reco2dur.write(f'{aid}\t{duration}\n')
                        for segment_file in segments_lists:
                            try:
                                sid = segment_file['sid']
                                start_time = segment_file['begin_time']
                                end_time = segment_file['end_time']
                                dur = end_time - start_time
                                text = segment_file['text']
                                segment_subsets = segment_file["subsets"]
                            except Exception:
                                print(f'''Warning: {segment_file} something
                                          is wrong, skipped''')
                                continue
                            else:
                                utt2text.write(f'{sid}\t{text}\n')
                                segments.write(
                                    f'{sid}\t{aid}\t{start_time}\t{end_time}\n'
                                )
                                utt2dur.write(f'{sid}\t{dur}\n')
                                segment_sub_names = " ".join(segment_subsets)
                                utt2subsets.write(
                                    f'{sid}\t{segment_sub_names}\n')


def main():
    args = get_args()

    meta_analysis(args.input_json, args.output_dir, args.pipe_format)


if __name__ == '__main__':
    main()
