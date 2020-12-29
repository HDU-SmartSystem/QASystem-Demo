import os

import ahocorasick


class QuestionClassifier:
    def __init__(self):
        cur_dir = '/'.join(os.path.abspath(__file__).split('/')[:-1])
        '''特征词路径'''
        self.name_path = os.path.join(cur_dir, 'dict/names.txt')
        self.address_path = os.path.join(cur_dir, 'dict/address.txt')
        self.tag_path = os.path.join(cur_dir, 'dict/tags.txt')
        '''加载特征词'''
        self.name_wds = [i.strip() for i in open(self.name_path, encoding="GBK") if i.strip()]
        self.address_wds = [i.strip() for i in open(self.address_path, encoding="GBK") if i.strip()]
        self.tag_wds = [i.strip() for i in open(self.tag_path, encoding="GBK") if i.strip()]
        self.rate_wds = ['评分', '质量评分', '服务评分', '分数', '环境评分']
        self.prob_wds = ['大于', '小于', '超过', '最高', '最低']
        self.region_words = set(
            self.name_wds + self.address_wds + self.tag_wds + self.rate_wds + self.prob_wds)

        '''构造领域actree'''
        self.region_tree = self.build_actree(list(self.region_words))

        '''构建词典'''
        self.wdtype_dict = self.build_wdtype_dict()

        '''问句疑问词'''
        self.names_qwds = ['名称', '名字', '叫什么', '是什么', '店铺', '商店']
        self.address_qwds = ['在哪', '什么位置', '位置', '怎么去']
        self.tag_qwds = {'属于什么', '属于', '什么标签', '什么分类', '什么类', '标签', '分类'}
        self.rate_qwds = {'评分', '质量评分', '服务评分', '环境评分', '分数', '分', '是多少', '大于', '小于', '超过', '最高', '最低'}

        print('model init finished ......')
        return

    '''分类主函数'''

    def classify(self, question):
        data = {}
        data['question'] = question
        market_dict = self.check_question(question)
        if not market_dict:
            return {}
        data['args'] = market_dict
        # 收集问句当中所涉及到的实体类型
        types = []
        for type_ in market_dict.values():
            types += type_

        question_type = 'others'
        question_types = []

        # 名字
        if self.check_words(self.names_qwds, question) and ('address' in types):
            question_type = 'address_to_name'
            question_types.append(question_type)

        if self.check_words(self.names_qwds, question) and ('tag' in types) and ('rate' not in types):
            question_type = 'tag_to_name'
            question_types.append(question_type)

        if self.check_words(self.names_qwds, question) and ('rate' in types) and ('address' not in types) and ('tag' not in types):
            question_type = 'rate_to_name'
            question_types.append(question_type)

        # 地址
        if self.check_words(self.address_qwds, question) and ('name' in types):
            question_type = 'name_to_address'
            question_types.append(question_type)

        if self.check_words(self.address_qwds, question) and ('rate' in types) and ('address' in types):
            question_type = 'address_to_name'
            question_types.append(question_type)

        if self.check_words(self.address_qwds, question) and ('tag' in types) and ('rate' not in types):
            question_type = 'tag_to_name'
            question_types.append(question_type)

        # 标签/分类
        if self.check_words(self.tag_qwds, question) and ('name' in types):
            question_type = 'name_to_tag'
            question_types.append(question_type)

        if self.check_words(self.tag_qwds, question) and ('address' in types):
            question_type = 'address_to_tag'
            question_types.append(question_type)

        if self.check_words(self.tag_qwds, question) and ('rate' in types) and ('tag' not in types) and ('name' not in types):
            question_type = 'rate_to_tag'
            question_types.append(question_type)

        # 评分
        if self.check_words(self.rate_qwds, question) and ('name' in types):
            question_type = 'name_to_rate'
            question_types.append(question_type)

        if self.check_words(self.rate_qwds, question) and ('address' in types):
            question_type = 'address_to_name'
            question_types.append(question_type)

        if self.check_words(self.rate_qwds, question) and ('tag' in types):
            question_type = 'tag_to_rate'
            question_types.append(question_type)

        # 将多个分类结果进行合并处理，组装成一个字典
        data['question_types'] = set(question_types)

        return data

    '''构造ac自动机 通常应用在问答系统中用于提取语句的关键词'''

    def build_actree(self, wordlist):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''构造词对应的类型'''

    def build_wdtype_dict(self):
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.name_wds:
                wd_dict[wd].append('name')
            if wd in self.address_wds:
                wd_dict[wd].append('address')
            if wd in self.tag_wds:
                wd_dict[wd].append('tag')
            if wd in self.rate_wds:
                wd_dict[wd].append('rate')
            if wd in self.prob_wds:
                wd_dict[wd].append('prob')
        return wd_dict

    '''问句过滤'''

    def check_question(self, question):
        region_wds = []
        for i in self.region_tree.iter(question):
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i: self.wdtype_dict.get(i) for i in final_wds}

        return final_dict

    '''基于特征词进行分类'''

    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False


if __name__ == '__main__':
    classifier = QuestionClassifier()
    print(classifier.check_question("属于化妆品的商店，评分最高是多少"))
    print("============= 基础问答 =================")
    print(classifier.classify("美宝莲纽约和自然堂在哪，他的评分怎么样，属于什么类"))
    print(classifier.classify("在下沙龙湖金沙天街是什么，他的评分是多少"))
    print("==============================")
    print(classifier.classify("评分大于7分的店铺有什么"))
    print(classifier.classify("评分大于7分的店铺在哪"))
    print(classifier.classify("属于化妆品的商店有什么"))
    print(classifier.classify("属于化妆品的商店在哪"))
    print("==============================")
    print(classifier.classify("属于化妆品的商店，评分最高的在哪"))
    print(classifier.classify("评分最高的化妆品的商店"))
    print(classifier.classify("属于化妆品的商店评分是多少"))
    print("==============================")
    print(classifier.classify("评分最高的商店在哪"))