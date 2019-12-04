import pandas as pd


class DbAnalysis:

    CACHE = {}

    def __init__(self, db_connect):
        self.db_connection_str = db_connect

    def get_table_data(self, table_name):
        if table_name not in self.CACHE.keys():
            self.CACHE[table_name] = pd.read_sql_table(table_name, self.db_connection_str)
        return self.CACHE[table_name]

    def get_user_id_by_name(self, username):
        users = self.get_table_data('users')
        u_id = users.loc[users['name'] == username]['id']
        return u_id.array[0] if len(u_id) > 0 else None

    def get_history_hist_data(self):
        data = self.get_table_data('history')
        return data['datetime'].to_list()
        # return [d.date() for d in data['datetime'].to_list()]

    def get_message_stats_by_name(self, username):
        u_id = self.get_user_id_by_name(username)
        if not u_id:
            return

        users = self.get_table_data('users')
        msgs = self.get_table_data('user_messages')
        msgs = msgs.loc[msgs['sender_id'] == u_id]
        u_msg = pd.merge(users, msgs, left_on='id', right_on='recipient_id')
        return u_msg.groupby('name').count()['text'].to_dict()
        # return list(u_msg['name'])
