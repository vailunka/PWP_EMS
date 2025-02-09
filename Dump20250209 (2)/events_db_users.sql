-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: events_db
-- ------------------------------------------------------
-- Server version	8.0.41

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(128) NOT NULL,
  `email` varchar(128) NOT NULL,
  `phone_number` varchar(128) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Beth Brown','hancockvanessa@example.com','+1-748-393-2866'),(2,'Mrs. Laura Clay','angelabutler@example.org','759-300-4315x818'),(3,'Sandra Harris','tricia63@example.org','(431)792-4649x70108'),(4,'Daryl Buckley','raustin@example.net','001-923-973-4008x89694'),(5,'Steven Carson','laurenanderson@example.com','5083228168'),(6,'Kevin King','malikadkins@example.com','913-774-0775'),(7,'Lindsay Howard','tyler14@example.org','(534)581-3500x520'),(8,'Karen Roberts','gary74@example.net','232.527.4961'),(9,'Cody Rodriguez','derek96@example.com','+1-870-322-5906x29659'),(10,'Katherine Smith','newmanfrank@example.net','646.811.2648x2464'),(11,'Ann Williams','alexmiller@example.net','001-214-239-7083x0042'),(12,'Blake Rogers','murraylori@example.net','(245)913-2117'),(13,'Brandon Cohen','jonestyler@example.com','847.833.4018'),(14,'David Acosta','autumn51@example.com','523.264.8710'),(15,'Laura Jones','cochranrachel@example.com','749.514.5399'),(16,'Anthony Smith','jacksonsarah@example.com','+1-287-399-2401x4900'),(17,'Daniel Smith','haley88@example.com','382-488-7010x812'),(18,'Joel Acosta','bennettmark@example.org','436.473.2588'),(19,'Sharon Sanchez','annewebb@example.net','656.969.8765'),(20,'Jessica Evans','kellyrobinson@example.net','222-736-0578x67463'),(21,'Michelle Leon','fordjulia@example.com','(731)411-4336x719'),(22,'Anthony Barker','ncook@example.com','(458)740-4657'),(23,'Melanie Murillo','kstein@example.org','+1-683-958-3854x27834'),(24,'James Zimmerman','morenobrittney@example.org','254.723.5363'),(25,'Dawn Davenport','ydavid@example.net','595.337.6675x739'),(26,'Stacy Mason MD','jacksonmcmillan@example.net','(987)676-3908x9248'),(27,'Shelley Castro','eric06@example.net','001-382-877-8269'),(28,'Robert Rhodes','kingernest@example.org','233.909.9148x58233'),(29,'Michael Rivera','erik92@example.org','9629683404');
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

-- Dump completed on 2025-02-09 20:09:13
