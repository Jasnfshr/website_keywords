setwd('/home/max/workspace/webclass/keyword_training')

dat = read.csv('keyword_data.csv')

library(MASS)

model = glm(is_keyword ~ (tf + df + in_url + in_title + in_hyperlink + pos)*(tf + df + in_url + in_title + in_hyperlink + pos),data=dat)

sm = step(model)

library(pROC)

prob = predict(sm,type=c('response'))
sm$prob = prob
g = roc(is_keyword ~ prob, data = dat)
plot(g)