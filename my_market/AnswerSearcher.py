from py2neo import Graph


class AnswerSearcher:
    def __init__(self):
        self.g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="123456789a")

    '''执行cypher查询，并返回相应结果'''

    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                res = self.g.run(query).data()
                answers += res
            final_answer = self.answer_prettify(question_type, answers)
            final_answers.append(final_answer)
        return final_answers

    '''根据对应的qustion_type，调用相应的回复模板'''

    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'name_to_address':
            desc = [i['address'] for i in answers]
            final_answer = '该商店位置在{0}处'.format(",".join(desc))

        if question_type == 'name_to_rate':
            desc = [i['rate'] for i in answers]
            final_answer = '评分为{0}分'.format(",".join(desc))

        if question_type == 'name_to_tag':
            desc = [i['tag'] for i in answers]
            final_answer = '所属类是{0}'.format(",".join(desc))

        if question_type == 'address_to_name':
            desc = [['名称:' + i['name'], '评分为:' + i['rate'], '属于:' + i['tag']] for i in answers]
            answer = ""
            for i in desc:
                answer += '店铺详情 {0}'.format(",".join(i)) + '\n'
            final_answer = answer

        if question_type == 'tag_to_name':
            desc = [['名称:' + i['name'], '地址:' + i['address'], '评分为:' + i['rate']] for i in answers]
            answer = ""
            for i in desc:
                answer += '店铺详情 {0}'.format(",".join(i)) + '\n'
            final_answer = answer

        if question_type == 'rate_to_name':
            desc = [['名称:' + i['name'], '地址:' + i['address'], '属于:' + i['tag'], '评分为:' + i['rate']] for i in answers]
            answer = ""
            for i in desc:
                answer += '店铺详情 {0}'.format(",".join(i)) + '\n'
            final_answer = answer

        print(question_type)
        if question_type == 'tag_to_rate':
            desc = [['名称:' + i['name'], '地址:' + i['address'],'评分为:' + i['rate']] for i in answers]
            answer = ""
            for i in desc:
                answer += '店铺详情 {0}'.format(",".join(i)) + '\n'
            final_answer = answer

        return final_answer


if __name__ == '__main__':
    searcher = AnswerSearcher()
    print(searcher.g.run(
        "MATCH (a:Address) - [l:locates_to] - (n:Name) WHERE a.name= '龙湖金沙天街B1' WITH  n MATCH p=(n) -[r*..1]-() return p").data())
