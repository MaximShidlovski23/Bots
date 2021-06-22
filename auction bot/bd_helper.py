import psycopg2
from datetime import datetime

conn = psycopg2.connect(host="localhost", port=5432, database="auction", user="postgres", password="2311")
print("Database opened successfully")

arr_keys = ['id', 'name', 'description', 'end_time', 'current_price', 'min_price_increase', 'image',
            'condition', 'start_price']


class BD:

    @staticmethod
    def get_category():
        try:
            cur = conn.cursor()
            cur.execute("""SELECT id, name FROM auction_category""")
            conn.commit()
            query_results = cur.fetchall()
            cur.close()
            arr_res = [', '.join(map(str, x)) for x in query_results]
            arr_id = []
            arr_category = []
            for res in arr_res:
                num = res.find(',')
                arr_id.append(res[:num])
                arr_category.append(res[num + 2:])
            return arr_id, arr_category
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def get_subcategory(category):
        try:
            cur = conn.cursor()
            sql_query = f"SELECT auction_subcategory.id, auction_subcategory.name " \
                        f"FROM auction_subcategory " \
                        f"INNER JOIN auction_category " \
                        f"ON auction_subcategory.category_id = auction_category.id " \
                        f"WHERE auction_category.name = '{category}'"
            cur.execute(sql_query)
            conn.commit()
            query_results = cur.fetchall()
            cur.close()
            arr_res = [', '.join(map(str, x)) for x in query_results]
            arr_id = []
            arr_subcategory = []
            for res in arr_res:
                num = res.find(',')
                arr_id.append(res[:num])
                arr_subcategory.append(res[num + 2:])
            return arr_subcategory
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def get_some_lots(telegram_id, subcategory):
        try:
            cur = conn.cursor()
            sql_query_select = f"SELECT id " \
                               f"FROM auction_account " \
                               f"WHERE telegram_id = '{telegram_id}' "
            cur.execute(sql_query_select)
            query_results = cur.fetchall()
            if query_results:
                id_user = query_results[0][0]
                sql_query_lot = f"SELECT auction_product.id, auction_product.name, auction_product.description, " \
                                f"auction_product.end_time, auction_product.current_price, " \
                                f"auction_product.min_price_increase, auction_product.image, condition, " \
                                f"auction_product.start_price " \
                                f"FROM auction_product " \
                                f"INNER JOIN auction_subcategory " \
                                f"ON auction_product.subcategory_id = auction_subcategory.id " \
                                f"WHERE is_active = true AND (last_bet_user_id != '{id_user}'" \
                                f"OR last_bet_user_id IS NULL)" \
                                f"AND auction_subcategory.name = '{subcategory}' " \
                                f"ORDER BY auction_product.end_time " \
                                f"LIMIT 5"
            else:
                sql_query_lot = f"SELECT auction_product.id, auction_product.name, auction_product.description, " \
                                f"auction_product.end_time, auction_product.current_price, " \
                                f"auction_product.min_price_increase, auction_product.image, condition, " \
                                f"auction_product.start_price " \
                                f"FROM auction_product " \
                                f"INNER JOIN auction_subcategory " \
                                f"ON auction_product.subcategory_id = auction_subcategory.id " \
                                f"WHERE is_active = true " \
                                f"AND auction_subcategory.name = '{subcategory}' " \
                                f"ORDER BY auction_product.end_time " \
                                f"LIMIT 5"
            cur.execute(sql_query_lot)
            conn.commit()
            query_results = cur.fetchall()
            cur.close()
            arr_results = []
            for i in range(len(query_results)):
                arr_result = []
                for res in query_results[i]:
                    arr_result.append(res)
                dict_results = dict(zip(arr_keys, arr_result))
                if dict_results['condition'] == 'Used':
                    dict_results['condition'] = 'Б\У'
                else:
                    dict_results['condition'] = 'Новое'
                arr_results.append(dict_results)
            return arr_results
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def get_random_lot(telegram_id):
        try:
            cur = conn.cursor()
            sql_query_select = f"SELECT id " \
                               f"FROM auction_account " \
                               f"WHERE telegram_id = '{telegram_id}' "
            cur.execute(sql_query_select)
            query_results = cur.fetchall()
            if query_results:
                id_user = query_results[0][0]
                sql_query = f"SELECT id, name, description, end_time, current_price, " \
                            f"min_price_increase, image, condition, start_price " \
                            f"FROM auction_product " \
                            f"WHERE is_active = true AND (last_bet_user_id != '{id_user}' " \
                            f"OR last_bet_user_id IS NULL)" \
                            f"ORDER BY RANDOM()" \
                            f"LIMIT 1"
            else:
                sql_query = f"SELECT id, name, description, end_time, current_price, " \
                            f"min_price_increase, image, condition, start_price " \
                            f"FROM auction_product " \
                            f"WHERE is_active = true " \
                            f"ORDER BY RANDOM()" \
                            f"LIMIT 1"
            conn.commit()
            cur.execute(sql_query)
            i = 0
            query_results = cur.fetchall()
            cur.close()
            arr_results = []
            for res in query_results[0]:
                arr_results.append(res)
                i += 1
            dict_results = dict(zip(arr_keys, arr_results))
            if dict_results['condition'] == 'Used':
                dict_results['condition'] = 'Б\У'
            else:
                dict_results['condition'] = 'Новое'
            return dict_results
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def get_nearest_lot(telegram_id):
        try:
            cur = conn.cursor()
            sql_query_select = f"SELECT id " \
                               f"FROM auction_account " \
                               f"WHERE telegram_id = '{telegram_id}' "
            cur.execute(sql_query_select)
            query_results = cur.fetchall()
            if query_results:
                id_user = query_results[0][0]
                sql_query = f"SELECT id, name, description, end_time, current_price, " \
                            f"min_price_increase, image, condition, start_price " \
                            f"FROM auction_product " \
                            f"WHERE is_active = true AND (last_bet_user_id != '{id_user}'" \
                            f"OR last_bet_user_id IS NULL)" \
                            f"ORDER BY end_time " \
                            f"LIMIT 1"
            else:
                sql_query = f"SELECT id, name, description, end_time, current_price, " \
                            f"min_price_increase, image, condition, start_price " \
                            f"FROM auction_product " \
                            f"WHERE is_active = true " \
                            f"ORDER BY end_time " \
                            f"LIMIT 1"
            cur.execute(sql_query)
            i = 0
            query_results = cur.fetchall()
            print(query_results)
            arr_results = []
            for res in query_results[0]:
                arr_results.append(res)
                i += 1
            dict_results = dict(zip(arr_keys, arr_results))
            print('=' * 20)
            print(dict_results)
            if dict_results['condition'] == 'Used':
                dict_results['condition'] = 'Б\У'
            else:
                dict_results['condition'] = 'Новое'
            return dict_results
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def get_image_cur_price_lot(id_lot):
        try:
            cur = conn.cursor()
            sql_query = f"SELECT name, image, current_price, description " \
                        f"FROM auction_product " \
                        f"WHERE id = '{id_lot}' "
            cur.execute(sql_query)
            conn.commit()
            cur.execute(sql_query)
            query_results = cur.fetchall()
            cur.close()
            arr_results = []
            for res in query_results[0]:
                arr_results.append(res)
            arr_small_keys = ['name', 'image', 'current_price', 'description']
            dict_results = dict(zip(arr_small_keys, arr_results))
            print(dict_results)
            return dict_results
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def binding_account(auth_code, telegram_id):
        try:
            cur = conn.cursor()
            sql_query_select = f"SELECT id, username, is_telegram_auth " \
                               f"FROM auction_account " \
                               f"WHERE telegram_code = '{auth_code}' "
            cur.execute(sql_query_select)
            cur.execute(sql_query_select)
            query_results = cur.fetchall()
            if not query_results:
                return None
            arr_results = []
            for res in query_results[0]:
                arr_results.append(res)
            arr_small_keys = ['id', 'username', 'is_telegram_auth']
            dict_results = dict(zip(arr_small_keys, arr_results))
            if not dict_results['is_telegram_auth']:
                sql_query_update = f"UPDATE auction_account " \
                                   f"SET is_telegram_auth = True, telegram_id = '{telegram_id}' " \
                                   f"WHERE telegram_code = '{auth_code}'"
                cur.execute(sql_query_update)
            conn.commit()
            cur.close()
            return dict_results
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def sold_now(id_lot, telegram_id, final_price):
        try:
            cur = conn.cursor()
            sql_query_select = f"SELECT id, username " \
                               f"FROM auction_account " \
                               f"WHERE telegram_id = '{telegram_id}' "
            cur.execute(sql_query_select)
            cur.execute(sql_query_select)
            query_results = cur.fetchall()
            arr_results = []
            for res in query_results[0]:
                arr_results.append(res)
            arr_small_keys = ['id', 'username']
            dict_results = dict(zip(arr_small_keys, arr_results))
            print(dict_results)
            if dict_results['id']:
                sql_query_update = f"UPDATE auction_product " \
                                   f"SET is_active = False, last_bet_user_id = '{dict_results['id']}', " \
                                   f"start_price = '{final_price}'" \
                                   f"WHERE id = '{id_lot}'"
                cur.execute(sql_query_update)
            else:
                print('не привязан к телеграму')
            conn.commit()
            cur.close()
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def is_telegram_auth(telegram_id):
        try:
            cur = conn.cursor()
            sql_query_select = f"SELECT is_telegram_auth " \
                               f"FROM auction_account " \
                               f"WHERE telegram_id = '{telegram_id}' "
            cur.execute(sql_query_select)
            conn.commit()
            cur.execute(sql_query_select)
            query_results = cur.fetchall()
            cur.close()
            print(query_results)
            return query_results
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()

    @staticmethod
    def place_bet(product_id, bet_price, telegram_id):
        try:
            cur = conn.cursor()
            sql_query_select = f"SELECT id " \
                               f"FROM auction_account " \
                               f"WHERE telegram_id = '{telegram_id}' "
            cur.execute(sql_query_select)
            query_results = cur.fetchall()
            id_user = query_results[0][0]
            sql_query_select = f"SELECT start_price  " \
                               f"FROM auction_product " \
                               f"WHERE id = '{product_id}' "
            cur.execute(sql_query_select)
            query_results = cur.fetchall()
            start_price = query_results[0][0]
            if int(start_price) >= int(bet_price):
                cur.close()
                return False
            sql_query_update = f"UPDATE auction_product " \
                               f"SET start_price = '{bet_price}', last_bet_user_id = '{id_user}' " \
                               f"WHERE id = '{product_id}'"
            cur.execute(sql_query_update)
            sql_insert_bet = f"INSERT INTO auction_bethistory " \
                             f"(bet, date, product_id, user_id) " \
                             f"VALUES ('{bet_price}', now(), '{product_id}', '{id_user}')"
            cur.execute(sql_insert_bet)
            conn.commit()
            cur.close()
            return True
        except psycopg2.DatabaseError as error:
            print(error)
            conn.rollback()
            return False

    @staticmethod
    def get_some_lots_with_history(telegram_id):
        try:
            cur = conn.cursor()
            sql_query_bet = f"SELECT product_id, max(bet), max(user_id) " \
                            f"FROM public.auction_bethistory " \
                            f"INNER JOIN public.auction_account " \
                            f"ON public.auction_bethistory.user_id = public.auction_account.id " \
                            f"WHERE public.auction_account.telegram_id = '{telegram_id}' " \
                            f"GROUP BY product_id HAVING COUNT(*)>=1 "
            cur.execute(sql_query_bet)
            query_results = cur.fetchall()
            arr_results_bet = []
            arr_keys_bet = ['product_id', 'my_bet', 'user_id']
            for i in range(len(query_results)):
                arr_result_bet = []
                for res in query_results[i]:
                    arr_result_bet.append(res)
                dict_results_bet = dict(zip(arr_keys_bet, arr_result_bet))
                arr_results_bet.append(dict_results_bet)
            # print(arr_results_bet)
            arr_results = []
            arr_keys_lot = ['id', 'name', 'description', 'end_time', 'current_price', 'min_price_increase', 'image',
                            'condition', 'last_bet_user_id', 'start_price']
            for arr_res in arr_results_bet:
                sql_query_lot = f"SELECT public.auction_product.id, public.auction_product.name, " \
                                f"description, end_time, " \
                                f"current_price, min_price_increase, " \
                                f"image, condition, last_bet_user_id, " \
                                f"start_price " \
                                f"FROM public.auction_product " \
                                f"WHERE is_active = True and id = '{arr_res['product_id']}' "
                cur.execute(sql_query_lot)
                conn.commit()
                query_results_lot = cur.fetchall()
                print(query_results_lot)
                for i in range(len(query_results_lot)):
                    arr_result = []
                    for res in query_results_lot[i]:
                        arr_result.append(res)
                    dict_results = dict(zip(arr_keys_lot, arr_result))
                    if dict_results['condition'] == 'Used':
                        dict_results['condition'] = 'Б\У'
                    else:
                        dict_results['condition'] = 'Новое'
                    arr_results.append(dict_results)
            cur.close()
            arr_lot_user = []
            sort_arr_results = sorted(arr_results, key=lambda k: k['end_time'])
            for arr in sort_arr_results:
                arr_lot_user.append(arr['last_bet_user_id'])
            arr_bet_user = []
            for arr in arr_results_bet:
                arr_bet_user.append(arr['user_id'])
            bool_arr = []
            arr_lose = []
            stats = [0, 0]
            for i in range(len(arr_bet_user)):
                if arr_lot_user[i] == arr_bet_user[i]:
                    bool_arr.append(True)
                    stats[0] += 1
                else:
                    bool_arr.append(False)
                    arr_lose.append(arr_results_bet[i]['my_bet'])
                    stats[1] += 1
            return sort_arr_results, bool_arr, arr_lose, stats
        except psycopg2.DatabaseError as error:
            conn.rollback()
            print(error)
