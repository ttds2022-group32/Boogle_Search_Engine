python url_extract.py "urls_list_new.txt"
python get_diff_url.py "urls_list.txt" "urls_list_new.txt"
FILE="urls_list_diff.txt"
if [ -e $FILE ]; then
  echo "Change exists."
  python scrape_full.py "urls_list_diff.txt"
  rm urls_list.txt
  rename "s/list_new/list/;" urls_list_new.txt
  python textPreProcessing.py
  python write_index_lists.py
