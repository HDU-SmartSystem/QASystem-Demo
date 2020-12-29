import os

from py2neo import Graph, Node
import json


class MarketGraph:

    def __init__(self):
        self.g = Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j",  # 数据库user name，如果没有更改过，应该是neo4j
            password="123456789a")

    # 读取 data
    def read_data(self):
        names = []
        address = []
        tags = []
        quality_rates = []
        environment_rates = []
        service_rates = []

        rels_name_address = []
        rels_name_tag = []
        rels_name_quality_rate = []
        rels_name_environment_rate = []
        rels_name_service_rate = []

        with open("../data/beauty_second.json", encoding='UTF-8') as f:
            load_dict = json.load(f)
        all_data = load_dict['RECORDS']
        for data in all_data:
            names.append(data['name'])
            address.append(data['address'])
            tags.append(data['tag'])
            quality_rates.append(data['quality_rate'])
            environment_rates.append(data['environment_rate'])
            service_rates.append(data['service_rate'])
            rels_name_address.append([data['name'], data['address']])
            rels_name_tag.append([data['name'], data['tag']])
            rels_name_quality_rate.append([data['name'], data['quality_rate']])
            rels_name_environment_rate.append([data['name'], data['environment_rate']])
            rels_name_service_rate.append([data['name'], data['service_rate']])
        return set(names), set(address), set(tags), set(quality_rates), set(environment_rates), set(service_rates), \
               rels_name_address, rels_name_tag, rels_name_quality_rate, rels_name_environment_rate, \
               rels_name_service_rate

    # 批量创建 node
    def create_node(self, label, nodes):
        for node_name in nodes:
            node = Node(label, name=node_name)
            self.g.create(node)

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        count = 0
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        all = len(set(set_edges))
        for edge in set(set_edges):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.g.run(query)
                count += 1
                print(rel_type, count, all)
            except Exception as e:
                print(e)
        return

    def export_data(self):
        names, address, tags, quality_rates, environment_rates, service_rates, rels_name_address, rels_name_tag, \
        rels_name_quality_rate, rels_name_environment_rate, rels_name_service_rate = self.read_data()
        f_name = open('dict/names.txt', 'w+')
        f_address = open('dict/address.txt', 'w+')
        f_tags = open('dict/tags.txt', 'w+')
        f_quality_rate = open('dict/quality_rates.txt', 'w+')
        f_environment_rate = open('dict/environment_rates.txt', 'w+')
        f_service_rate = open('dict/service_rates.txt', 'w+')

        f_name.write('\n'.join(list(names)))
        f_address.write('\n'.join(list(address)))
        f_tags.write('\n'.join(list(tags)))
        f_quality_rate.write('\n'.join(list(quality_rates)))
        f_environment_rate.write('\n'.join(list(environment_rates)))
        f_service_rate.write('\n'.join(list(service_rates)))

        f_name.close()
        f_address.close()
        f_tags.close()
        f_quality_rate.close()
        f_environment_rate.close()
        f_service_rate.close()
        return


if __name__ == '__main__':
    handle = MarketGraph()
    handle.export_data()
    # names, address, tags, quality_rates, environment_rates, service_rates, rels_name_address, rels_name_tag, \
    # rels_name_quality_rate, rels_name_environment_rate, rels_name_service_rate = handle.read_data()
    # handle.create_node('Name', names)
    # handle.create_node('Address', address)
    # handle.create_node('Tag', tags)
    # handle.create_node('Quality', quality_rates)
    # handle.create_node('Environment', environment_rates)
    # handle.create_node('Service', service_rates)
    # handle.create_relationship('Name', 'Address', rels_name_address, 'locates_to', '地址')
    # handle.create_relationship('Name', 'Tag', rels_name_tag, 'belongs_to', '标签')
    # handle.create_relationship('Name', 'Quality', rels_name_quality_rate, 'quality_rate', '质量评分')
    # handle.create_relationship('Name', 'Environment', rels_name_environment_rate, 'environment_rate', '环境评分')
    # handle.create_relationship('Name', 'Service', rels_name_service_rate, 'service_rate', '服务评分')
