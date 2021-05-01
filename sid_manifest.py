import os
from pathlib import Path
import pandas as pd

# os.system('wget http://www02.smt.ufrj.br/~igor.quintanilha/sid.tar.gz')

## Attention to the folder M0049 that contains M0001 inside, it is duplicated, an action is needed
## For this dataset, I've decided to remove, but you should take note and do another action if you'd like to keep it.

folder = Path('sid/')
paths = list(folder.glob('*/*.wav'))
otherpaths = list(folder.glob('*/*/*.wav'))
paths.extend(otherpaths)

prompts = list(folder.glob('*/prompts.txt'))
otherprompts = list(folder.glob('*/*/prompts.txt'))
prompts.extend(otherprompts)

wav_paths = []
transcript_texts = []

for prompt in prompts:
    with open(prompt, 'r', encoding="utf-8") as file:
        full_prefix = f"{'/'.join(prompt.as_posix().split('/')[0:2])}/{prompt.as_posix().split('/')[1]}0"
        temp_lines = file.readlines()
        new_paths = [full_prefix + (line.split('=')[0]).zfill(2) + '.wav' for i, line in enumerate(temp_lines)]
        texts = [(line.split('=')[1]).rstrip() for i, line in enumerate(temp_lines)]
        wav_paths.extend(new_paths)
        transcript_texts.extend(texts)

df = pd.DataFrame({'wav_paths': wav_paths, 'transcript_texts': transcript_texts})

df['new_wav_paths'] = df['wav_paths'].apply(
                            lambda x: Path(
                                f"{x.split('/')[0]}/audios/{x.split('/')[-1]}"
                            ).with_suffix('.flac').as_posix())

for i, audio in enumerate(df['wav_paths']):
    if not os.path.exists('sid/audios'):
        os.mkdir('sid/audios')
    command = f"ffmpeg -i {audio} -ar 16000 {df['new_wav_paths'][i]}"
    os.system(command)

dirs = os.listdir('sid/')
dirs.remove('audios')

removed_dirs = [os.system(f'rm -rf sid/{directory}') for directory in dirs]

[os.system(f"rm -rf {row}") for row in [df[df['transcript_texts'] == '']['new_wav_paths']]]

df = df[df['transcript_texts'] != ''].reset_index(drop=True)

final_df = df[['new_wav_paths', 'transcript_texts']]
final_df.columns = ['wav_paths', 'transcripts']
for audio in final_df['wav_paths']:
    if not os.path.exists(audio):
        final_df = final_df[final_df['wav_paths'] != audio]

final_df.to_csv('sid/transcripts.tsv', sep='\t', encoding='utf-8')