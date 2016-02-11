args<-commandArgs(TRUE)
require(stringr)
block_id = as.character(args[1])
bs = str_pad(block_id,3,pad="0")
require(pROC)
setwd('/home/max/workspace/webclass')

load('keyword_training/roc_environment.rdata')

test_data = read.csv('webpages/keyword_data.csv')

new_odds_ratios = predict(sm,test_data)
keydata = test_data[new_odds_ratios >= selected_threshold,c('file_id','gram')]
keydata$preds = new_odds_ratios[new_odds_ratios >= selected_threshold]
write.csv(paste0('webpages/keyword_file_',bs,'.csv'),row.names = FALSE)
print("wrote keywords to csv")