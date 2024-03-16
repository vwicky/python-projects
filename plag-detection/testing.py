from document_similarity import *
from document_cooker import *
from additional_functions.time_cheker import *
from setting_files.saved_pathes import *

name_list = ['first text', 'second text']
text_list = ['Hi, nice to see you again, Paul',
             'Hi, nice to see you again, ',
             'bozhe, tse zh w mene kyivstar :<',
             'Good evening! nice to see you again, Sofia']

param = Parameters(
    token='letter',
    k_shingles= 2,
    hf_amount= 50,
    buckets_amount= 10,
    bucket_size= 5
)

doc_sim = DocumentSimilarity(name_list, text_list, param)

# print('\nthreshold = ', doc_sim.calc_threshold())

# time_checker = TimeChecker()

# doc_sim.form_document_sketches_list()
# doc_sim.find_consecutive_pairs()
# similar_docs = doc_sim.form_similar_docs_list()

# time_checker.check_last_time().print_time('calculations finished')
    
# print('\nUnwrapped')
# for key, value in similar_docs:
#     print(key, ' -> ', value)
