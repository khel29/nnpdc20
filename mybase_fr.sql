-- MySQL dump 10.18  Distrib 10.3.27-MariaDB, for debian-linux-gnueabihf (armv8l)
--
-- Host: localhost    Database: mybasefr
-- ------------------------------------------------------
-- Server version	10.3.27-MariaDB-0+deb10u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `blacklist`
--

DROP TABLE IF EXISTS `blacklist`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `blacklist` (
  `id_blacklist` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_from` bigint(10) NOT NULL,
  `id_to` bigint(10) NOT NULL,
  PRIMARY KEY (`id_blacklist`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `blacklist`
--

LOCK TABLES `blacklist` WRITE;
/*!40000 ALTER TABLE `blacklist` DISABLE KEYS */;
/*!40000 ALTER TABLE `blacklist` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gender`
--

DROP TABLE IF EXISTS `gender`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gender` (
  `gender_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `gender_desc` varchar(100) NOT NULL,
  `used` bigint(10) DEFAULT 0,
  PRIMARY KEY (`gender_id`),
  UNIQUE KEY `gender_desc` (`gender_desc`)
) ENGINE=InnoDB AUTO_INCREMENT=32 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gender`
--

LOCK TABLES `gender` WRITE;
/*!40000 ALTER TABLE `gender` DISABLE KEYS */;
INSERT INTO `gender` VALUES (14,'Default',1),(21,'Tous',1),(22,'Neutre',1),(23,'Transgenre',1),(24,'Aucun',1),(25,'Non connu',1),(26,'Non binaire',1),(27,'Homme',4),(28,'Femme',4),(29,'Lesbienne',1),(30,'Gay',1),(31,'Bi',1);
/*!40000 ALTER TABLE `gender` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interests`
--

DROP TABLE IF EXISTS `interests`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `interests` (
  `interest_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `interest_desc` varchar(100) NOT NULL,
  `used` bigint(10) DEFAULT 0,
  PRIMARY KEY (`interest_id`),
  UNIQUE KEY `interest_desc` (`interest_desc`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interests`
--

LOCK TABLES `interests` WRITE;
/*!40000 ALTER TABLE `interests` DISABLE KEYS */;
INSERT INTO `interests` VALUES (17,'Default',1),(18,'Video Games',1),(20,'Shopping',3),(21,'Trekking',1),(23,'Tennis',1),(24,'Nature',3),(25,'La cafetière du futur',1),(26,'Lecture',3),(27,'Musique',3),(28,'Vélo',1),(29,'Course à pieds',3),(30,'Echecs',1),(31,'Surf',1),(32,'Amis',3),(33,'Gėnėalogie',1),(34,'Photo',1);
/*!40000 ALTER TABLE `interests` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `messages`
--

DROP TABLE IF EXISTS `messages`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `messages` (
  `message_id` bigint(10) NOT NULL AUTO_INCREMENT,
  `id_fromuser` bigint(10) NOT NULL,
  `id_touser` bigint(10) NOT NULL,
  `message` varchar(512) DEFAULT NULL,
  `image_uuid` varchar(32) NOT NULL,
  `rank_to` int(11) NOT NULL,
  `image_load_counter` int(11) NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`message_id`)
) ENGINE=InnoDB AUTO_INCREMENT=256 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `messages`
--

LOCK TABLES `messages` WRITE;
/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `status`
--

DROP TABLE IF EXISTS `status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `status` (
  `status_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `status_desc` varchar(100) NOT NULL,
  `used` bigint(10) DEFAULT 0,
  PRIMARY KEY (`status_id`),
  UNIQUE KEY `status_desc` (`status_desc`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `status`
--

LOCK TABLES `status` WRITE;
/*!40000 ALTER TABLE `status` DISABLE KEYS */;
INSERT INTO `status` VALUES (1,'Star',1),(11,'Default',1),(16,'Pas tes oignons',1),(17,'Célibataire',1),(19,'Marrié(e)',4),(20,'Barbare',1),(22,'En couple',4),(23,'Pacsé(e)',1),(24,'Magicien(ne)',1);
/*!40000 ALTER TABLE `status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `user_id` bigint(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `birthday` datetime NOT NULL,
  `comment` varchar(230) DEFAULT NULL,
  `firstconnection` datetime NOT NULL,
  `lastconnection` datetime DEFAULT NULL,
  `gender_id` bigint(20) NOT NULL,
  `interests_id` bigint(20) NOT NULL,
  `status_id` bigint(20) NOT NULL,
  `locationlat` decimal(9,6) DEFAULT NULL,
  `locationlong` decimal(9,6) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `pwdhash` varchar(100) NOT NULL,
  `notification` int(11) DEFAULT 0,
  `nbrconns` int(11) DEFAULT 0,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (20,'Niakniak','1977-05-03 00:00:00','Développeur de cette appli','2021-05-03 01:54:20','2021-05-30 02:44:31',27,24,19,48.102570,-4.338150,'nnpdc@ninipeaudchien.org','d43061298b53cc8f77bef3e646184465a4e4c495',0,18),(22,'BigDadou','1991-12-09 00:00:00','Je supporte pas le café','2021-05-03 17:23:45','2021-05-03 22:17:12',14,25,11,48.316600,-4.281000,'davaine.francois@hotmail.fr','55af5e84fe43fac3b9c22915463b0a9a27440575',0,0),(23,'Geopot','1948-06-18 00:00:00','Joueur de billard','2021-05-09 18:09:18','2021-05-12 21:30:38',27,33,19,48.107210,-4.352870,'Gp@yopmail.com','46a4064453a2d04541af55941d8611032a147443',0,0);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-05-30  3:32:10
