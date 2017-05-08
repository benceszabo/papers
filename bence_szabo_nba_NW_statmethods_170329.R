#In this program file I am going to execute the network analysis of 
#the NBA mentor-mentee network created by the code bence_szabo_nba_scrape_statmethods.py
# We are going to load in a directed network, and compute several NW statistics
#Most important one: eigenvector centrality.

#Bence Szabó, 2017.03.25.

rm(list = ls())

library(foreign)
library(igraph)
root = "C:/Users/bence/Dropbox/Egyetem_13_szemeszter/StatMethods/project"
setwd(root)

#load the data
df_links <- read.csv("df_links.csv", sep = ";", header = TRUE)

mentor_names <-aggregate(df_links$dOWS, by=list(df_links$Mentor,df_links$MentorID), 
                    FUN=mean)
mentor_names <- mentor_names[, 1:2]
colnames(mentor_names) <- c("Mentor","MentorID")

elist <- as.matrix(df_links[, c(6:7)])
elist_names <- as.matrix(df_links[, c(1:2)])

#weights: offense and defense
dOWS <- df_links[, 4]
dDWS <- df_links[, 5]

#create igraph Objects
gO <-graph.data.frame(elist, directed=TRUE)
E(gO)$weight <- dOWS
gD <-graph.data.frame(elist, directed=TRUE)
E(gD)$weight <- dDWS

#####################################################################
#TO DO: test with Random Matrix Theory whether link is non0
#####################################################################

#create a RMT with mean and variance of the values
AM <- as_adjacency_matrix(gO, attr = "weight", sparse = FALSE)
m <- mean(AM)
sd <- sd(AM)
AM2 <- abs(AM - m) / sd
#if it is within 2 sd-s => 0
AM[AM2 < 2] <- 0

#recreate the graph: Offense
gO <- graph_from_adjacency_matrix(AM, mode = "directed", weighted = TRUE)

#create a RMT with mean and variance of the values
AM <- as_adjacency_matrix(gD, attr = "weight", sparse = FALSE)
m <- mean(AM)
sd <- sd(AM)
AM2 <- abs(AM - m) / sd
#if it is within 2 sd-s => 0
AM[AM2 < 2] <- 0

#Defense graph
gD <- graph_from_adjacency_matrix(AM, mode = "directed", weighted = TRUE)

##########################
#1. Eigenvector approach
##########################
#OFFENSE
#players who were less than 3 years in the leauge will have no indegree
ev_centdOWS <- eigen_centrality(gO, directed = TRUE, weights = E(gO)$weight)
ev_c <- as.data.frame(ev_centdOWS$vector)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("OEvector_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)

#offensive eigenvector centrality
DII <- merge.data.frame(ev_c, mentor_names, x.by=ev_c$MentorID, y.by=mentor_names$MentorID)

#DEFENSE
ev_centdDWS <- eigen_centrality(gD, directed = TRUE, weights = E(gD)$weight)
ev_c <- as.data.frame(ev_centdDWS$vector)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("DEvector_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)

#defensive eigenvector centrality
DII <- merge.data.frame(DII, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)


##########################
#2. Degree approach
##########################

#OFFENSE
#players who were less than 3 years in the league will have no indegree
d_centdOWS <- graph.strength(gO, mode = "in", weights = gO$weight)
ev_c <- as.data.frame(d_centdOWS)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("OWDegree_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)
#offensive eigenvector centrality
DII <- merge.data.frame(DII, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)

#DEFENSE
d_centdDWS <- graph.strength(gD, mode = "in", weights = gD$weight)
ev_c <- as.data.frame(d_centdDWS)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("DWDegree_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)
#defensive eigenvector centrality
DII <- merge.data.frame(DII, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)

#################################################################
#3. Normalize by total number of degrees:
#solving problem of journeymen, BEFORE computing the centralities
#################################################################
#simple indegree
#OFFENSE
d_cent <- degree(gO, mode = "in")

ev_c <- as.data.frame(d_cent)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("ODegree_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)

DII <- merge.data.frame(DII, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)

#DEFENSE
d_cent <- degree(gD, mode = "in")

ev_c <- as.data.frame(d_cent)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("DDegree_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)

DII <- merge.data.frame(DII, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)

####################################################################################
#Separate the groups: we always leave out nodes which have a low degree
####################################################################################

#LIST OF coaches wrt offense and defense
DII_coaches <- DII[DII$MentorID >= 100000, ]
DII_players <- DII[DII$MentorID < 100000, ]

#################################################
#II. ALTERNATIVE VERSION: standardized WS 
#################################################

#load the data
df_links_v2 <- read.csv("df_links_v2.csv", sep = ";", header = TRUE)

mentor_names <-aggregate(df_links_v2$dOWS, by=list(df_links$Mentor,df_links$MentorID), 
                         FUN=mean)
mentor_names <- mentor_names[, 1:2]
colnames(mentor_names) <- c("Mentor","MentorID")

elist <- as.matrix(df_links_v2[, c(6:7)])
elist_names <- as.matrix(df_links_v2[, c(1:2)])

#weights: offense and defense
dOWS <- df_links_v2[, 4]
dDWS <- df_links_v2[, 5]

#create igraph Objects
gO <-graph.data.frame(elist, directed=TRUE)
E(gO)$weight <- dOWS
gD <-graph.data.frame(elist, directed=TRUE)
E(gD)$weight <- dDWS

#####################################################################
#dismissing small weight links
#####################################################################

#if it is within 2 SD, we will not use it
AM <- as_adjacency_matrix(gO, attr = "weight", sparse = FALSE)
m <- mean(AM)
sd <- sd(AM)
AM2 <- abs(AM - m) / sd
#if it is within 2 sd-s => 0
AM[AM2 < 2] <- 0

#recreate the graph: Offense
gO <- graph_from_adjacency_matrix(AM, mode = "directed", weighted = TRUE)

#create a RMT with mean and variance of the values
AM <- as_adjacency_matrix(gD, attr = "weight", sparse = FALSE)
m <- mean(AM)
sd <- sd(AM)
AM2 <- abs(AM - m) / sd
#if it is within 2 sd-s => 0
AM[AM2 < 2] <- 0

#Defense graph
gD <- graph_from_adjacency_matrix(AM, mode = "directed", weighted = TRUE)

##########################
#1. Eigenvector approach
##########################
#OFFENSE
#players who were less than 3 years in the leauge will have no indegree
ev_centdOWS <- eigen_centrality(gO, directed = TRUE, weights = E(gO)$weight)
ev_c <- as.data.frame(ev_centdOWS$vector)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("OEvector_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)
#offensive eigenvector centrality
DII2 <- merge.data.frame(ev_c, mentor_names, x.by=ev_c$MentorID, y.by=mentor_names$MentorID)

#DEFENSE
ev_centdDWS <- eigen_centrality(gD, directed = TRUE, weights = E(gD)$weight)
ev_c <- as.data.frame(ev_centdDWS$vector)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("DEvector_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)
#defensive eigenvector centrality
DII2 <- merge.data.frame(DII2, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)

##########################
#2. Degree approach
##########################

#OFFENSE
#players who were less than 3 years in the league will have no indegree
d_centdOWS <- graph.strength(gO, mode = "in", weights = gO$weight)
ev_c <- as.data.frame(d_centdOWS)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("OWDegree_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)
#offensive eigenvector centrality
DII2 <- merge.data.frame(DII2, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)

#DEFENSE
d_centdDWS <- graph.strength(gD, mode = "in", weights = gD$weight)
ev_c <- as.data.frame(d_centdDWS)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("DWDegree_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)
#defensive eigenvector centrality
DII2 <- merge.data.frame(DII2, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)

#################################################################
#3. Normalize by total number of degrees:
#solving problem of journeymen, BEFORE computing the centralities
#################################################################
#simple indegree
#OFFENSE
d_cent <- degree(gO, mode = "in")

ev_c <- as.data.frame(d_cent)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("ODegree_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)

DII2 <- merge.data.frame(DII2, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)

#DEFENSE
d_cent <- degree(gD, mode = "in")

ev_c <- as.data.frame(d_cent)
ev_c$ID <- rownames(ev_c)
colnames(ev_c) <- c("DDegree_cent", "MentorID")
ev_c$MentorID <- as.integer(ev_c$MentorID)

DII2 <- merge.data.frame(DII2, ev_c, x.by=DII$MentorID, y.by=ev_c$MentorID, all.x = TRUE)


####################################################################################
#Separate the groups: we always leave out nodes which have a low degree
####################################################################################

#LIST OF coaches wrt offense and defense
DII2_coaches <- DII2[DII2$MentorID >= 100000, ]
DII2_players <- DII2[DII2$MentorID < 100000, ]

####################################################
#III. TRANSITIVITY / BALANCE EXAMINATION
####################################################

mean(transitivity(gO, type = "weighted", weights = NULL), na.rm = TRUE)
mean(transitivity(gD, type = "weighted", weights = NULL), na.rm = TRUE)


#player stats:
player_stats <- read.csv("df_nba_stats.csv", sep = ";", header = TRUE)

#ATTACH COACH STATISTICS, CREATE ONE SINGLE DATASET
coach_stats <- read.csv("df_coaches_stat.csv", sep = ";", header = TRUE)
names(coach_stats) <- c("X", "Mentor", "WL_pc")

DII_coaches <- merge.data.frame(DII_coaches, coach_stats, x.by=DII_coaches$Mentor, y.by=coach_stats$Mentor, all.x = TRUE)
DII2_coaches <- merge.data.frame(DII2_coaches, coach_stats, x.by=DII2_coaches$Mentor, y.by=coach_stats$Mentor, all.x = TRUE)

#################
#PLOTS
#################

#baseline
coachplotO <- ggplot(data = DII_coaches, aes(x = OEvector_cent, y = WL_pc, label=Mentor)) +
    geom_point() +
    geom_text(data = subset(DII_coaches, OEvector_cent > 0.25), vjust=0)
coachplotO
ggsave("coachplotOclear.png")

coachplotD <- ggplot(data = DII_coaches, aes(x = DEvector_cent, y = WL_pc, label=Mentor)) +
    geom_point() +
    geom_text(data = subset(DII_coaches, DEvector_cent > 0.1), vjust=0)
coachplotD
ggsave("coachplotDclear.png")

coachplot_both <- ggplot(data = DII_coaches, aes(x = OEvector_cent, y = DEvector_cent, label=Mentor)) +
    geom_point() +
    geom_text(data = subset(DII_coaches, DEvector_cent > 0.1), vjust=0)
coachplot_both
ggsave("coachplot_bothclear.png")


#baseline
playerplot_both <- ggplot(data = DII_players, aes(x = OEvector_cent, y = DEvector_cent, label=Mentor)) +
    geom_point() +
    geom_text(data = subset(DII_players, DEvector_cent > 0.1), vjust=0)
playerplot_both
ggsave("playerplot_bothclear.png")




#standardized
coachplotO2 <- ggplot(data = DII2_coaches, aes(x = OEvector_cent, y = WL_pc, label=Mentor)) +
    geom_point() +
    geom_text(data = subset(DII2_coaches, OEvector_cent > 0.25), vjust=0)
coachplotO2
ggsave("coachplotO2clear.png")
coachplotD2 <- ggplot(data = DII2_coaches, aes(x = DEvector_cent, y = WL_pc, label=Mentor)) +
    geom_point() +
    geom_text(data = subset(DII2_coaches, DEvector_cent > 0.1), vjust=0)
coachplotD2
ggsave("coachplotD2clear.png")
coachplot_both2 <- ggplot(data = DII2_coaches, aes(x = OEvector_cent, y = DEvector_cent, label=Mentor)) +
    geom_point() +
    geom_text(data = subset(DII2_coaches, DEvector_cent > 0.1), vjust=0)
coachplot_both
ggsave("coachplot_both2clear.png")






