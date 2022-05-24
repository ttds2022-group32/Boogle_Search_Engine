import sys
import os

original = sys.argv[1]
new_one = sys.argv[2]

with open(original, "r", encoding="utf-8") as f:
    original_urls_list = f.read()
    original_urls_list = urls_list.split("\n")

with open(new_one, "r", encoding="utf-8") as f:
    new_urls_list = f.read()
    new_urls_list = urls_list.split("\n")

diff_urls = list(set(new_urls_list) - set(original_urls_list))
diff_urls = [x+"\n" for x in diff_urls]

if diff_urls != []:
    with open("urls_list_diff.txt", "r", encoding="utf-8") as f:
        f.writelines(diff_urls)
else:
    if os.path.exists("urls_list_diff.txt"): os.remove("urls_list_diff.txt")
    else: pass
