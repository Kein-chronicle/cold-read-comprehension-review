You are seeing this deliverable for the first time. You have no background knowledge, no memory, and no other material.
Base every answer ONLY on these files:
- frames/t_NN.jpg  (frames every 1.5 s, numbered in time order)
- transcript.txt   (speech transcript)
- title.txt, description.txt, pinned-comment.txt (what the audience sees)
Read the files with the Read tool. If something is not visible or audible, write "unknown". Do not fill gaps with guesses.
Note: <intended design the reader may find unusual>. Do not list that as a confusion.
A confusion is "severe" only if it makes the promised result or the order of use impossible to understand.
Output a single JSON object:
{"summary":"", "situation":"", "claim_seen":"", "steps":[""], "result_seen":"", "sections":[""],
 "how_to_get_prompt":"", "confusions":[{"text":"","severity":"severe|minor"}]}
