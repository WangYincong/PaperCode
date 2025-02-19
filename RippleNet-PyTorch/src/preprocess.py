# ratings.dat  用户id, 电影id, 评分, 时间戳
# item_index2entity_id_rehashed.txt：ratings文件中的item在KG中对应的entity。

import argparse
import numpy as np

RATING_FILE_NAME = dict({'movie': 'ratings.dat', 'book': 'BX-Book-Ratings.csv', 'news': 'ratings.txt'})
SEP = dict({'movie': '::', 'book': ';', 'news': '\t'})
THRESHOLD = dict({'movie': 4, 'book': 0, 'news': 0})


def read_item_index_to_entity_id_file():
    file = '../data/' + DATASET + '/item_index2entity_id_rehashed.txt'
    print('reading item index to entity id file: ' + file + ' ...')
    i = 0
    for line in open(file, encoding='utf-8').readlines():
        item_index = line.strip().split('\t')[0]
        satori_id = line.strip().split('\t')[1]
        item_index_old2new[item_index] = i
        entity_id2index[satori_id] = i
        i += 1


def convert_rating():
    file = '../data/' + DATASET + '/' + RATING_FILE_NAME[DATASET]

    print('reading rating file ...')
    print('reading rating file ...')
    item_set = set(item_index_old2new.values())
    # print(item_index_old2new)
    user_pos_ratings = dict()
    user_neg_ratings = dict()

    for line in open(file, encoding='utf-8').readlines()[1:]:
        # print(line)
        # print(SEP[DATASET])
        array = line.strip().split(SEP[DATASET])
        # print(array)
        # break
        # remove prefix and suffix quotation marks for BX dataset
        if DATASET == 'book':
            array = list(map(lambda x: x[1:-1], array))

        item_index_old = array[1]

        if item_index_old not in item_index_old2new:  # the item is not in the final item set
            continue  # 如果这个if不成立，会跳过当前循环剩余内容执行下一次循环

        item_index = item_index_old2new[item_index_old]

        user_index_old = int(array[0])
        # print(user_index_old)
        rating = float(array[2])
        # print(rating)
        if rating >= THRESHOLD[DATASET]:
            if user_index_old not in user_pos_ratings:
                user_pos_ratings[user_index_old] = set()
            user_pos_ratings[user_index_old].add(item_index)
        else:
            if user_index_old not in user_neg_ratings:
                user_neg_ratings[user_index_old] = set()
            user_neg_ratings[user_index_old].add(item_index)
    # print(user_pos_ratings)
    # print(user_neg_ratings)
    print('converting rating file ...')
    writer = open('../data/' + DATASET + '/ratings_final.txt', 'w', encoding='utf-8')
    user_cnt = 0
    user_index_old2new = dict()
    for user_index_old, pos_item_set in user_pos_ratings.items(): # items以列表返回可遍历的（键值）元组数组
        if user_index_old not in user_index_old2new:
            # 将用户的旧索引 user_index_old 映射到新的用户索引 user_cnt 上，并将 user_cnt 增加 1，以便为下一个用户分配新的索引。
            user_index_old2new[user_index_old] = user_cnt
            user_cnt += 1
        user_index = user_index_old2new[user_index_old] # 获取用户的新的索引 user_index

        for item in pos_item_set:
            writer.write('%d\t%d\t1\n' % (user_index, item))
        unwatched_set = item_set - pos_item_set # set集合减法

        # 如果用户有负向评分(user_neg_ratings)，则将这些负向评分的物品从，unwatched_set中去除，表示这些物品不能作为负样本。
        if user_index_old in user_neg_ratings:
            unwatched_set -= user_neg_ratings[user_index_old]
        for item in np.random.choice(list(unwatched_set), size=len(pos_item_set), replace=False):
            writer.write('%d\t%d\t0\n' % (user_index, item))
    writer.close()
    print('number of users: %d' % user_cnt)
    print('number of items: %d' % len(item_set))


def convert_kg():
    print('converting kg file ...')
    # print(entity_id2index)
    entity_cnt = len(entity_id2index)
    relation_cnt = 0

    writer = open('../data/' + DATASET + '/kg_final.txt', 'w', encoding='utf-8')

    files = []
    该这里
    if DATASET == 'movie':
        files.append(open('../data/' + DATASET + '/kg_part1_rehashed.txt', encoding='utf-8'))
        files.append(open('../data/' + DATASET + '/kg_part2_rehashed.txt', encoding='utf-8'))
    else:
        files.append(open('../data/' + DATASET + '/kg_rehashed.txt', encoding='utf-8'))

    for file in files:
        for line in file:
            array = line.strip().split('\t')
            head_old = array[0]
            relation_old = array[1]
            tail_old = array[2]

            if head_old not in entity_id2index:
                entity_id2index[head_old] = entity_cnt
                entity_cnt += 1
            head = entity_id2index[head_old]

            if tail_old not in entity_id2index:
                entity_id2index[tail_old] = entity_cnt
                entity_cnt += 1
            tail = entity_id2index[tail_old]

            if relation_old not in relation_id2index:
                relation_id2index[relation_old] = relation_cnt
                relation_cnt += 1
            relation = relation_id2index[relation_old]

            writer.write('%d\t%d\t%d\n' % (head, relation, tail))

    writer.close()
    print('number of entities (containing items): %d' % entity_cnt)
    print('number of relations: %d' % relation_cnt)


if __name__ == '__main__':
    np.random.seed(555)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', type=str, default='movie', help='which dataset to preprocess')
    args = parser.parse_args()
    DATASET = args.dataset

    entity_id2index = dict()
    relation_id2index = dict()
    item_index_old2new = dict()

    read_item_index_to_entity_id_file()

    # print(entity_id2index)
    # print(relation_id2index)
    # print(item_index_old2new)

    convert_rating()
    convert_kg()

    print('done')
