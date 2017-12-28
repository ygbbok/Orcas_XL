import pandas as pd

class DF_Util(object):
	@staticmethod
	def df_from_dictlist(dict_list_IN):
		res_df = pd.DataFrame()
		new_dict_value = None
		for dict_item in dict_list_IN:
			idx = dict_item[0]
			dict_value = dict_item[1]
			new_dict_value = {key: {idx : value} for key,value in dict_value.iteritems()}
			res_df = res_df.append(pd.DataFrame.from_dict(new_dict_value))
		return res_df


def main():

	dict_1 = {"IRR": 1, "PnL" : 4, "TEST" : 8}
	dict_2 = {"IRR": 1, "PnL" : 3, "TEST" : 10}
	dict_3 = {"IRR": 10, "PnL" : 4, "TEST" : 8}
	dict_4 = {"IRR": 100, "PnL" : 42, "TEST" : 1}

	dict_list = [dict_1, dict_2, dict_3, dict_4]

	a = DF_Util.df_from_dictlist(dict_list_IN = dict_list)
	print a

if __name__ == "__main__":
	main()