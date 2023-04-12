import pandas as pd

book_mapping = {}

with open(r"C:\Users\Ben\Desktop\gphc-data\inv_data_gr.csv", "r") as f:
    next(f)
    while True:
        line = f.readline()
        if not line:
            break
        item_id, _, _, _, gr_id, _ = line.strip().split(",")
        book_mapping[int(gr_id)] = int(item_id)

inter_df = pd.read_csv(r"C:\Users\Ben\Desktop\gphc-data\interactions.csv")

inter_df['item_id'] = inter_df['item_id'].map(book_mapping)

inter_df.to_csv('patron_data_gr.csv')

