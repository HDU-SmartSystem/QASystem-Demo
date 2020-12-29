import re


class QuestionParser:
    """构建实体节点"""

    def build_entitydict(self, args):
        entity_dict = {}
        for arg, types in args.items():
            for type in types:
                if type not in entity_dict:
                    entity_dict[type] = [arg]
                else:
                    entity_dict[type].append(arg)

        return entity_dict

    '''解析主函数'''

    def parser_main(self, res_classify):
        print(res_classify)
        args = res_classify['args']
        entity_dict = self.build_entitydict(args)
        entity_dict['question'] = res_classify['question']
        question_types = res_classify['question_types']
        sqls = []
        for question_type in question_types:
            sql_ = {}
            sql_['question_type'] = question_type
            sql = []
            '''基础问答'''
            if question_type == 'name_to_rate':
                sql = self.sql_transfer(question_type, entity_dict.get('name'))
            if question_type == 'name_to_address':
                sql = self.sql_transfer(question_type, entity_dict.get('name'))
            if question_type == 'name_to_tag':
                sql = self.sql_transfer(question_type, entity_dict.get('name'))
            if question_type == 'address_to_name':
                sql = self.sql_transfer(question_type, entity_dict.get('address'))
            '''抽象问答待优化'''
            if question_type == 'rate_to_name':
                sql = self.sql_transfer(question_type, entity_dict)
            if question_type == 'tag_to_name':
                sql = self.sql_transfer(question_type, entity_dict.get('tag'))
            if question_type == 'tag_to_rate':
                sql = self.sql_transfer(question_type, entity_dict)
            if sql:
                sql_['sql'] = sql
                sqls.append(sql_)
        print(sqls)
        return sqls

    '''针对不同的问题，分开进行处理'''

    def sql_transfer(self, question_type, entities):
        if not entities:
            return []

        # 查询语句
        sql = []

        '''基础问答'''
        if question_type == 'name_to_address':
            sql = ["MATCH (n:Name)-[l:locates_to]-(a:Address) WHERE n.name =~ '{0}.*' return a.name as address"
                       .format(i) for i in entities]

        if question_type == 'name_to_rate':
            sql = ["MATCH (n:Name)-[r:quality_rate]->(q:Quality) WHERE n.name =~ '{0}.*' RETURN q.name as rate"
                       .format(i) for i in entities]

        if question_type == 'name_to_tag':
            sql = ["MATCH (n:Name)-[r:belongs_to]->(t:Tag) WHERE n.name =~ '{0}.*' RETURN t.name as tag"
                       .format(i) for i in entities]

        if question_type == 'address_to_name':
            sql = ["MATCH (a:Address) - [l:locates_to] - (n:Name) WHERE a.name =~ '.*{0}.*' WITH " \
                   "n MATCH (n) -[:belongs_to]-(b), (n) -[:service_rate]-(s) " \
                   "return n.name as name,b.name as tag,s.name as rate".format(i) for i in entities]

        if question_type == 'tag_to_name':
            sql = ["MATCH (a:Tag) - [b:belongs_to] - (n:Name) WHERE a.name =~ '.*{0}.*' " \
                   "WITH n MATCH (n) -[:locates_to]-(b), (n) -[:service_rate]-(s)" \
                   " return n.name as name,b.name as address,s.name as rate".format(i) for i in entities]

        '''抽象问答待优化'''
        if question_type == 'rate_to_name':
            if 'prob' in entities.keys():
                scores = re.findall(r"\d+\.?\d*", entities.get('question'))
                if self.chose_compare(entities.get('prob')[0]) == '>':
                    sql = ["MATCH(p1:Environment)-[rel:environment_rate]-(n) where p1.name > '{0}' "
                           "WITH n MATCH (n) -[:locates_to]-(b), (n) -[:belongs_to]-(s), (n) -[:environment_rate]-(r)"
                           "return n.name as name,b.name as address,s.name as tag,r.name as rate order by rate desc"
                               .format(i) for i in scores]
                if self.chose_compare(entities.get('prob')[0]) == '<':
                    sql = ["MATCH(p1:Environment)-[rel:environment_rate]-(n) where p1.name < '{0}' "
                           "WITH n MATCH (n) -[:locates_to]-(b), (n) -[:belongs_to]-(s), (n) -[:environment_rate]-(r)"
                           "return n.name as name,b.name as address,s.name as tag,r.name as rate order by rate desc"
                               .format(i) for i in scores]
                if self.chose_compare(entities.get('prob')[0]) == '=':
                    sql = ["MATCH(p1:Environment)-[rel:environment_rate]-(n) where p1.name = '{0}' "
                           "WITH n MATCH (n) -[:locates_to]-(b), (n) -[:belongs_to]-(s), (n) -[:environment_rate]-(r)"
                           "return n.name as name,b.name as address,s.name as tag,r.name as rate order by rate desc"
                               .format(i) for i in scores]

                if entities.get('prob')[0] == '最高':
                    sql = ["MATCH(e:Environment) WITH MAX(e.name) AS max_rate "
                           "MATCH(p1:Environment)<-[rel:environment_rate]-(n) WHERE p1.name=max_rate "
                           "WITH n,p1 MATCH (n)-[:locates_to]->(b), (n)-[:belongs_to]->(s) "
                           "return n.name as name,b.name as address,s.name as tag,p1.name as rate "]
                if entities.get('prob')[0] == '最低':
                    sql = ["MATCH(e:Environment) WITH MIN(e.name) AS min_rate "
                           "MATCH(p1:Environment)<-[rel:environment_rate]-(n) WHERE p1.name=min_rate "
                           "WITH n,p1 MATCH (n)-[:locates_to]->(b), (n)-[:belongs_to]->(s) "
                           "return n.name as name,b.name as address,s.name as tag,p1.name as rate "]

        if question_type == 'tag_to_rate':
            if 'prob' in entities.keys():
                if entities.get('prob')[0] == '最高':
                    sql = ["MATCH (n)-[:belongs_to]->(s) WHERE s.name = '{0}' " \
                           "WITH n MATCH (n)-[:environment_rate]->(r)WITH MAX(r.name) AS max_rate " \
                           "MATCH(p1:Environment)<-[rel:environment_rate]-(c) WHERE p1.name=max_rate " \
                           "WITH c,p1 MATCH (c)-[:locates_to]->(b)" \
                           "RETURN c.name as name,b.name as address,p1.name as rate"
                               .format(i) for i in entities.get('tag')]
                if entities.get('prob')[0] == '最低':
                    sql = ["MATCH (n)-[:belongs_to]->(s) WHERE s.name = '{0}' " \
                           "WITH n MATCH (n)-[:environment_rate]->(r) WITH MIN(r.name) AS min_rate " \
                           "MATCH(p1:Environment)<-[rel:environment_rate]-(c) WHERE p1.name=min_rate " \
                           "WITH c,p1 MATCH (c)-[:locates_to]->(b)" \
                           "RETURN c.name as name,b.name as address,p1.name as rate"
                               .format(i) for i in entities.get('tag')]

            else:
                sql = ["MATCH (n)-[:belongs_to]->(s) WHERE s.name = '{0}' " \
                       "WITH n MATCH (n)-[:environment_rate]->(r) ,(n)-[:locates_to]->(b) " \
                       "RETURN n.name as name,b.name as address,r.name as rate"
                           .format(i) for i in entities.get('tag')]

        return sql

    def chose_compare(self, prob):
        index = {'大于': '>', '超过': '>', '小于': '<', '低于': '<', '等于': '=', '最高': 'order by rate desc limit 1',
                 '最低': 'order by rate limit 1'}
        return index[prob]
