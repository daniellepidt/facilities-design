import pickle

with open('storage_list.p', 'rb') as file:
  storage_list = pickle.load(file)

print("storage_list")
print(storage_list)


sum_of_items = sum([x[1] for x in storage_list])
print(sum_of_items)

with open('prob_list.p', 'rb') as file:
  prob_list = pickle.load(file)

print("prob_list")
print(prob_list)