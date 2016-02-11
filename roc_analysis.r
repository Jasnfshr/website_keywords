require(pROC)

setwd('/home/max/workspace/webclass/keyword_training')

dat = read.csv('keyword_data.csv',encoding='utf-8')

model = glm(is_keyword ~ (tf + df + in_url + in_title + in_hyperlink + pos)*(tf + df + in_url + in_title + in_hyperlink + pos),data=dat)

print('finished full model')
sm = step(model)
print('made stepwise model')

prob = predict(sm,type=c('response'))
sm$prob = prob
print('generating ROC values (this will take a while)')
g = roc(is_keyword ~ prob, data = dat)
print('generated ROC values')
#library(ggplot2)
#library(reshape2)

nf = data.frame(threshold = g$threshold,sensitivity = g$sensitivities,specificity = g$specificities)
#nf = melt(nf,id.var = 'threshold')
total_p = sum(dat$is_keyword)
total_n = nrow(dat) - total_p
pf = nf
pf$tp = pf$sensitivity * total_p
pf$tn = pf$specificity * total_n
pf$fp = (total_n-pf$tn)
pf$ppv = pf$tp/(pf$tp + pf$fp)

#select best threshold
selected_threshold = pf$threshold[which.max(pf$ppv)]
new_threshold = pf$threshold[pf$ppv >= 0.15][which.min(pf$threshold[pf$ppv >= 0.15])]
if (length(new_threshold) > 0)
  selected_threshold = new_threshold
sum(sm$prob*(dat$is_keyword) > new_threshold)
sum(sm$prob*(1-dat$is_keyword) > new_threshold)
print('selected optimal threshold')
#this will be reloaded when general classification is performed
save.image('roc_environment.rdata')
print('saved ROC R environment data')
#run this if you've uncommented the melt function the line after nf is created
#ggplot(nf,aes(x=threshold,y=value,color=variable))+geom_line()
#plot(g)