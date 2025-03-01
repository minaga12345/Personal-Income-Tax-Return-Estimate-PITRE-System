-- MySQL dump 10.13  Distrib 9.0.1, for Win64 (x86_64)
--
-- Host: localhost    Database: tax_system
-- ------------------------------------------------------
-- Server version	9.0.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `payroll_records`
--

DROP TABLE IF EXISTS `payroll_records`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payroll_records` (
  `id` int NOT NULL AUTO_INCREMENT,
  `person_id` varchar(10) DEFAULT NULL,
  `pay_period_start` date DEFAULT NULL,
  `pay_period_end` date DEFAULT NULL,
  `gross_income` decimal(10,2) DEFAULT NULL,
  `tax_paid` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `person_id` (`person_id`),
  CONSTRAINT `payroll_records_ibfk_1` FOREIGN KEY (`person_id`) REFERENCES `users` (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=110 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payroll_records`
--

LOCK TABLES `payroll_records` WRITE;
/*!40000 ALTER TABLE `payroll_records` DISABLE KEYS */;
INSERT INTO `payroll_records` VALUES (28,'user101','2024-01-01','2024-12-12',5000.00,100.00),(30,'123456','2024-02-01','2024-02-15',3000.00,360.00),(84,'123456','2024-03-01','2024-03-15',3000.00,360.00),(85,'123456','2024-03-16','2024-03-31',3000.00,360.00),(86,'123456','2024-04-01','2024-04-15',3000.00,360.00),(87,'123456','2024-04-16','2024-04-30',3000.00,360.00),(88,'123456','2024-05-01','2024-05-15',3000.00,360.00),(89,'123456','2024-05-16','2024-05-31',3000.00,360.00),(90,'123456','2024-06-01','2024-06-15',3000.00,360.00),(91,'123456','2024-06-16','2024-06-30',3000.00,360.00),(92,'123456','2024-07-01','2024-07-15',3000.00,360.00),(93,'123456','2024-07-16','2024-07-31',3000.00,360.00),(94,'123456','2024-08-01','2024-08-15',3000.00,360.00),(95,'123456','2024-08-16','2024-08-31',3000.00,360.00),(96,'123456','2024-09-01','2024-09-15',3000.00,360.00),(97,'123456','2024-09-16','2024-09-30',3000.00,360.00),(98,'123456','2024-10-01','2024-10-15',3000.00,360.00),(99,'123456','2024-10-16','2024-10-31',3000.00,360.00),(100,'123456','2024-11-01','2024-11-15',3000.00,360.00),(101,'123456','2024-11-16','2024-11-30',3000.00,360.00),(102,'123456','2024-12-01','2024-12-15',3000.00,360.00),(103,'123456','2024-12-16','2024-12-31',3000.00,360.00),(104,'123456','2025-01-01','2025-01-15',3000.00,360.00),(105,'123456','2025-01-16','2025-01-31',3000.00,360.00),(106,'123456','2025-02-01','2025-02-15',3000.00,360.00),(107,'123456','2025-02-16','2025-02-28',3000.00,360.00),(108,'123456','2025-03-01','2025-03-15',3000.00,360.00),(109,'123456','2025-01-01','2025-01-15',3000.00,360.00);
/*!40000 ALTER TABLE `payroll_records` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tax_history`
--

DROP TABLE IF EXISTS `tax_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tax_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `person_id` varchar(10) DEFAULT NULL,
  `calculation_date` datetime DEFAULT CURRENT_TIMESTAMP,
  `annual_income` decimal(10,2) DEFAULT NULL,
  `tax_withheld` decimal(10,2) DEFAULT NULL,
  `tax_amount` decimal(10,2) DEFAULT NULL,
  `is_refund` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `person_id` (`person_id`),
  CONSTRAINT `tax_history_ibfk_1` FOREIGN KEY (`person_id`) REFERENCES `users` (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tax_history`
--

LOCK TABLES `tax_history` WRITE;
/*!40000 ALTER TABLE `tax_history` DISABLE KEYS */;
INSERT INTO `tax_history` VALUES (5,'user101','2024-10-23 13:12:39',75000.00,10000.00,15875.00,0),(6,'user101','2024-10-23 13:21:44',48000.00,100.00,9310.00,0),(7,'user101','2024-10-24 18:50:12',75000.00,10000.00,15875.00,0),(8,'user101','2024-10-24 18:50:54',48000.00,100.00,9310.00,0);
/*!40000 ALTER TABLE `tax_history` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tfn_free_users`
--

DROP TABLE IF EXISTS `tfn_free_users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tfn_free_users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `person_id` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `person_id` (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tfn_free_users`
--

LOCK TABLES `tfn_free_users` WRITE;
/*!40000 ALTER TABLE `tfn_free_users` DISABLE KEYS */;
INSERT INTO `tfn_free_users` VALUES (1,'user109','userpass109','Olive Green','oilve.green@gmail.com','2024-10-23 13:34:16');
/*!40000 ALTER TABLE `tfn_free_users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `person_id` varchar(10) NOT NULL,
  `tfn` varchar(9) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `password` varchar(50) DEFAULT NULL,
  `role` enum('user','admin') NOT NULL DEFAULT 'user',
  `annual_income` decimal(10,2) DEFAULT NULL,
  `tax_withheld` decimal(10,2) DEFAULT NULL,
  `has_health_insurance` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `person_id` (`person_id`),
  UNIQUE KEY `person_id_2` (`person_id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (8,'admin001',NULL,'Admin User','admin@example.com','adminpass','admin',NULL,NULL,NULL),(9,'user101','47394759','Alice Johnson','alice.johnson@gmail.com','userpass101','user',75000.00,10000.00,1),(10,'user102',NULL,'Bob Smith','bob.smith@example.com','UserPass102','admin',85000.00,12000.00,0),(11,'user103',NULL,'Charlie Brown','charlie.brown@example.com','UserPass103','user',95000.00,15000.00,1),(12,'user104',NULL,'Diana Evans','diana.evans@example.com','UserPass104','user',65000.00,8000.00,0),(13,'user105',NULL,'Edward Wright','edward.wright@example.com','UserPass105','user',60000.00,6000.00,1),(14,'user106',NULL,'Fiona Lee','fiona.lee@example.com','UserPass106','user',70000.00,7000.00,0),(17,'user107','47392071','John Doe','john.doe@gmail.com','userpass107','user',100000.00,1000.00,1),(20,'user110','47502438','Kelly Reynolds','kelly.reynolds@gmail.com','userpass110','user',NULL,NULL,NULL),(25,'123456','123456789','John Doe','john.doe@example.com','password123','user',75000.00,10000.00,1),(29,'user113','20934856','Roman Row','roman.row@gmail.com','roman123','user',NULL,NULL,NULL);
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

-- Dump completed on 2024-10-25 20:58:58
