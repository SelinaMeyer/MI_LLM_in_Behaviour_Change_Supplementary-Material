library(tidyr)
library(car)
library(lmtest)
library(MASS)
library(sfsmisc)
library(gvlma)
library(LambertW)
library(PerformanceAnalytics)
library(dplyr)
library(irr)
library(caret)
library(psych)

setwd(dirname(rstudioapi::getActiveDocumentContext()$path))
dat <- read.csv(file='IRR_Results.csv', sep=",")
dat_R = dat[dat$Rater_1_topic == "R", ]
topic <- dat[c("Rater_2_topic", "Rater_1_topic")]
valence <- dat[c("Rater_2_valence", "Rater_1_valence")]
reason_type <- dat_R[c("Rater_2_reason_type", "Rater_1_reason_type")]

kappam.fleiss(valence, detail=TRUE)
kappam.fleiss(topic, detail=TRUE)
kappam.fleiss(reason_type, detail=TRUE)

