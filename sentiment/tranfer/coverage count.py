import re

def ReadInKeyWords(keywords_file):
    "This function is used to read in keywords"
    keywords_dict = dict()
    input_data = open(keywords_file, "r", encoding = "utf-8")
    for eachLine in input_data:
        if eachLine != "" and eachLine != "\n":
            input_str = eachLine.replace("\n", "")
            input_str = input_str.replace("\ufeff", "")
            fields = input_str.split("\t")
            field_name = fields[0]
            attr_name = field_name.split("_")[0]
            if attr_name not in keywords_dict.keys():
                keywords_dict[attr_name] = dict()
            word_type = field_name[len(attr_name)+1:]
            if word_type not in keywords_dict[attr_name].keys():
                keywords_dict[attr_name][word_type] = list()
            if len(fields) > 1:
                for eachWord in fields[1:]:
                    if eachWord != "" and eachWord not in keywords_dict[attr_name][word_type]:
                        keywords_dict[attr_name][word_type].append(eachWord)
    input_data.close()
    for eachAttr in keywords_dict.keys():
        for eachType in keywords_dict[eachAttr].keys():
            keywords_dict[eachAttr][eachType].sort(key = len, reverse = True)
    return keywords_dict


def RemoveStopWords(stopwords_file):
    "This function is used to remove stop words from the review"
    stopwords_list = list()
    input_file = open(stopwords_file, "r")
    for eachLine in input_file:
        if eachLine != "\n" and eachLine != "":
            words_str = eachLine.replace("\n", "")
            words_str = words_str.replace("\ufeff", "")
            words = words_str.split(",")
            for each in words:
                stopwords_list.append(each)
    input_file.close()
    stopwords_list.sort(key = len, reverse = True)
    return stopwords_list

def ReadInReviews(review_file):
    "This function is used to read reviews"
    sentences = list()
    punctuation = {" ", "，", "。", "！", "~", "@", "#", "￥", "%", "……", "&", "*", "（", "）", "？", "：", "；", ".", "...", "，", "。", "!", "～", "(", ")", "虽然", "但是", "不过", "但", "只是", "于是", "然后", "然而", "所以", "因为", "由于", "不管","啊","吗","呢","吧"}
    review_data = open(review_file, "r", encoding = "utf-8")
    for eachLine in review_data:
        if eachLine != "\n" and eachLine != "":
            small_sent = list()
            input_str = eachLine.replace("\n", "")
            input_str = input_str.replace("\ufeff", "")
            input_str = input_str.replace("\ue00e", "")
            input_str = input_str.replace('"', "")
            input_str = input_str.replace("'", "")
            if input_str != "":
                fields = input_str.split("\t")
                review = fields[5]
                cleaned_review = "".join(review)
                for eachPunc in punctuation:
                        if eachPunc in review:
                            cleaned_review = cleaned_review.replace(eachPunc, ",")
                split_review = cleaned_review.split(",")
                for eachOne in split_review:
                    if eachOne != '':
                        small_sent.append(eachOne)
            sentences.append([review, small_sent])
    review_data.close()
    return sentences

"！！！！！！！！！！！！！Please change the file:"
folder_address = "/Users/santostang/Desktop/"
keyword_file_name = "keyword.txt"
review_file_name = "reviews.txt"
stopword_file_name = "stop words.txt"
output_file_name = "result.txt"


"Read in keywords"
keywords_dict = ReadInKeyWords(folder_address + keyword_file_name)
keywords_list = list()
for eachAttr in keywords_dict.keys():
    for eachType in keywords_dict[eachAttr].keys():
        for eachWord in keywords_dict[eachAttr][eachType]:
            if eachWord != "" and eachWord not in keywords_list:
                keywords_list.append(eachWord)
keywords_list.sort(key = len, reverse = True)

"Read in reviews"
reviews = ReadInReviews(folder_address + review_file_name)
for eachone in reviews:
    eachReview = eachone[0]
    for eachSen in eachone[1]:
        if eachSen != "":
            words_list, words_type, words_index = list(), list(), list()
            noun_counter, adj_counter, adv_counter, verb_counter, conj_counter, keyword_counter = 0, 0, 0, 0, 0, 0
            "Remove stop words"
            stopwords_list = RemoveStopWords(folder_address + stopword_file_name)
            for eachWord in stopwords_list:
                if eachWord in eachSen:
                    eachSen = eachSen.replace(eachWord, "*"*len(eachWord))
            new_sentence = "".join(eachSen)
            buffer_sentence = "".join(eachSen)
            buffer_new_sentence = "".join(eachSen)
            for eachKeyWord in keywords_list:
                if eachKeyWord in buffer_sentence:
                    new_word = re.compile(eachKeyWord).findall(buffer_sentence)
                    for eachAttr in keywords_dict.keys():
                        for eachType in keywords_dict[eachAttr]:
                            if eachKeyWord in keywords_dict[eachAttr][eachType] and (eachType == "Neu_Noun" or eachType == "Pos_Noun" or eachType == "Neg_Noun"):
                                for each in re.compile(eachKeyWord).findall(buffer_sentence):
                                    eachIndex = buffer_sentence.index(each)
                                    new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "<" + eachKeyWord + ">" + new_sentence[buffer_new_sentence.index(each)+len(each):]
                                    buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(each) + buffer_sentence[eachIndex+len(each):]
                                    words_list.append(each)
                                    words_index.append(eachIndex)
                                    if eachType == "Neu_Noun":
                                        words_type.append("Neu_Noun")
                                    elif eachType == "Pos_Noun":
                                        words_type.append("Pos_Noun")
                                    elif eachType == "Neg_Noun":
                                        words_type.append("Neg_Noun")
                                    else:
                                        pass
                                noun_counter = noun_counter + len(new_word)
                            elif eachKeyWord in keywords_dict[eachAttr][eachType] and (eachType == "Pos_Verb" or eachType == "Neg_Verb"):
                                for each in re.compile(eachKeyWord).findall(buffer_sentence):
                                    eachIndex = buffer_sentence.index(each)
                                    new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "(" + eachKeyWord + ")" + new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(eachKeyWord) + buffer_sentence[eachIndex+len(eachKeyWord):]
                                    words_list.append(each)
                                    words_index.append(eachIndex)
                                    if eachType == "Pos_Verb":
                                        words_type.append("Pos_Verb")
                                    elif eachType == "Neg_Verb":
                                        words_type.append("Neg_Verb")
                                    else:
                                        pass
                                verb_counter = verb_counter + len(new_word)
                            elif eachKeyWord in keywords_dict[eachAttr][eachType] and (eachType == "Neu_Adj" or eachType == "Pos_Adj" or eachType == "Neg_Adj"):
                                for each in re.compile(eachKeyWord).findall(buffer_sentence):
                                    eachIndex = buffer_sentence.index(each)
                                    new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "[" + eachKeyWord + "]" + new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(eachKeyWord) + buffer_sentence[eachIndex+len(eachKeyWord):]
                                    words_list.append(each)
                                    words_index.append(eachIndex)
                                    if eachType == "Neu_Adj":
                                        words_type.append("Neu_Adj")
                                    elif eachType == "Pos_Adj":
                                        words_type.append("Pos_Adj")
                                    elif eachType == "Neg_Adj":
                                        words_type.append("Neg_Adj")
                                    else:
                                        pass
                                adj_counter = adj_counter + len(new_word)
                            elif eachKeyWord in keywords_dict[eachAttr][eachType] and (eachType == "Strong_Adv" or eachType == "Somewhat_Adv" or eachType == "Neg_Adv"):
                                for each in re.compile(eachKeyWord).findall(buffer_sentence):
                                    eachIndex = buffer_sentence.index(each)
                                    new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "{" + eachKeyWord + "}" + new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(eachKeyWord) + buffer_sentence[eachIndex+len(eachKeyWord):]
                                    words_list.append(each)
                                    words_index.append(eachIndex)
                                    if eachType == "Strong_Adv":
                                        words_type.append("Strong_Adv")
                                    elif eachType == "Somewhat_Adv":
                                        words_type.append("Somewhat_Adv")
                                    elif eachType == "Neg_Adv":
                                        words_type.append("Neg_Adv")
                                    else:
                                        pass
                                adv_counter = adv_counter + len(new_word)
                            elif eachKeyWord in keywords_dict[eachAttr][eachType] and eachType == "Conj":
                                for each in re.compile(eachKeyWord).findall(buffer_sentence):
                                    eachIndex = buffer_sentence.index(each)
                                    new_sentence = new_sentence[:buffer_new_sentence.index(each)] + "$" + eachKeyWord + "$" + new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_new_sentence = buffer_new_sentence[:buffer_new_sentence.index(each)] + "*"*(len(eachKeyWord)+2) + buffer_new_sentence[buffer_new_sentence.index(each)+len(eachKeyWord):]
                                    buffer_sentence = buffer_sentence[:eachIndex] + "*"*len(eachKeyWord) + buffer_sentence[eachIndex+len(eachKeyWord):]
                                    words_list.append(each)
                                    words_index.append(eachIndex)
                                    words_type.append("Conj")
                                conj_counter = conj_counter + len(new_word)        
                            else:
                                pass

            "calculate coverage"
            for each in words_list:
                keyword_counter = keyword_counter + len(each)
            if keyword_counter > 0 and len(eachSen) > 0:
                coverage = round(keyword_counter / len(eachSen), 2)
            else:
                coverage = 0

            "Sort words list, words type"
            for i in range(len(words_index)-1, 0, -1):
                for j in range(i):
                    if words_index[j] > words_index[j+1]:
                        words_index[j], words_index[j+1] = words_index[j+1], words_index[j]
                        words_list[j], words_list[j+1] = words_list[j+1], words_list[j]
                        words_type[j], words_type[j+1] = words_type[j+1], words_type[j]

            "Check double type"
            for i in range(len(words_list)):
                if "Verb" in words_type[i]:
                    for eachAttr in keywords_dict.keys():
                        for eachType in keywords_dict[eachAttr].keys():
                            if words_list[i] in keywords_dict[eachAttr][eachType] and "_Adj" in eachType:
                                if words_list[i] + "的" in eachSen:
                                    if eachType == "Neu_Adj":
                                        words_type[i] = "Neu_Adj"
                                    elif eachType == "Pos_Adj":
                                        words_type[i] = "Pos_Adj"
                                    else:
                                        words_type[i] = "Neg_Adj"
                                    verb_counter = verb_counter - 1
                                    adj_counter = adj_counter + 1
                                    new_sentence = new_sentence.replace("(" + words_list[i] + ")", "[" + words_list[i] + "]")
                                elif words_list[i] == eachSen[len(eachSen)-len(words_list[i]):]:
                                    if eachType == "Neu_Adj":
                                        words_type[i] = "Neu_Adj"
                                    elif eachType == "Pos_Adj":
                                        words_type[i] = "Pos_Adj"
                                    else:
                                        words_type[i] = "Neg_Adj"
                                    verb_counter = verb_counter - 1
                                    adj_counter = adj_counter + 1
                                    new_sentence = new_sentence.replace("(" + words_list[i] + ")", "[" + words_list[i] + "]")
                                else:
                                    pass
                            else:
                                pass
                elif "Adj" in words_type[i]:
                    for eachAttr in keywords_dict.keys():
                        for eachType in keywords_dict[eachAttr].keys():
                            if words_list[i] in keywords_dict[eachAttr][eachType] and "_Adv" in eachType:
                                if i < len(words_list)-1 and "_Adj" in words_type[i+1]:
                                    if (words_list[i] + words_list[i+1] in eachSen) or re.search(words_list[i] + "[^和与跟同及、]" + words_list[i+1], eachSen) is not None:
                                        if eachType == "Strong_Adv":
                                            words_type[i] = "Strong_Adv"
                                        elif eachType == "Somewhat_Adv":
                                            words_type[i] = "Somewhat_Adv"
                                        else:
                                            words_type[i] = "Neg_Adv"
                                        adj_counter = adj_counter - 1
                                        adv_counter = adv_counter + 1
                                        new_sentence = new_sentence.replace("[" + words_list[i] + "]", "{" + words_list[i] + "}")
                                    else:
                                        pass
                else:
                    pass

            "output result"
            output_file = open(folder_address + output_file_name, "a", encoding = "utf-8")
            output_str = eachReview + "\t" + eachSen + "\t" + new_sentence + "\t" + str(coverage) + "\t" + str(noun_counter) + "\t" + str(adj_counter) + "\t" + str(adv_counter) + "\t" + str(verb_counter) + "\t" + str(conj_counter) + "\r\n"
            output_file.write(output_str)
            output_file.close()
    

