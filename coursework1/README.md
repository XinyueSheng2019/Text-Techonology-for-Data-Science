Here are the steps to run these programs.

1. Add <root> and </root> at the top and bottom of original document xml file respectively.

2. In the terminal, please input 'python3  indexing.py  yourfile.xml', and then wait for the program to finish. For example:

   ~~~
   $python3  indexing.py  trec.sample.xml
   Programming starts.
   Save the result.
   Programming finished!
   ~~~

   Then, two files, 'index.txt' and 'index.json' will be generated.

3. input 'python3 BooleanSearch.py queries.boolean.txt '

   The file 'results.boolean.txt' will be generated.

4. input 'python3 RankQuery.py queries.ranked.txt'

   The file 'results.ranked.txt' will be generated.

