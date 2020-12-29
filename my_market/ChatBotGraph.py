from my_market.AnswerSearcher import AnswerSearcher
from my_market.QuestionClassifier import QuestionClassifier
from my_market.QuestionParser import QuestionParser


class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionParser()
        self.searcher = AnswerSearcher()

    def chat_main(self, sent):
        answer = '您好，我是智能助理，希望可以帮到您。如果没答上来，可联系工作人员。祝您身体棒棒！'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        res_sql = self.parser.parser_main(res_classify)
        final_answers = self.searcher.search_main(res_sql)
        if not final_answers:
            return answer
        else:
            return ','.join(final_answers)


if __name__ == '__main__':
    handler = ChatBotGraph()
    # print(handler.chat_main("美宝莲纽约在哪，他的评分怎么样，属于什么类"))
    # print(handler.chat_main("在龙湖金沙天街B1以及杭州下沙金沙湖1号2幢1915室的商店叫什么，怎么样"))
    # print(handler.chat_main("属于化妆品的商店在哪"))
    # print(handler.chat_main("评分大于7.5分的店铺有什么"))
    # print(handler.chat_main("属于美甲的商店评分最高是什么"))
    print(handler.chat_main("属于化妆品的商店评分是多少"))
