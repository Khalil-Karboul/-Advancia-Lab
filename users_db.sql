-- phpMyAdmin SQL Dump
-- version 5.0.4
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 19, 2021 at 11:42 AM
-- Server version: 8.0.23
-- PHP Version: 8.0.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `users_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `drill`
--

CREATE TABLE `drill` (
  `id` int NOT NULL,
  `training_name` varchar(20) DEFAULT NULL,
  `trainer_id` int DEFAULT NULL,
  `end_date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `drill`
--

INSERT INTO `drill` (`id`, `training_name`, `trainer_id`, `end_date`) VALUES
(1, 'Cisco', 1, '2021-04-13'),
(2, 'NSE4', 2, '2021-04-28'),
(3, 'CEH', 1, '2021-05-08'),
(4, 'CEH', 2, '2021-05-21'),
(5, 'Cisco', 2, '2021-06-18');

-- --------------------------------------------------------

--
-- Table structure for table `participant`
--

CREATE TABLE `participant` (
  `id` int NOT NULL,
  `firstname` varchar(30) NOT NULL,
  `lastname` varchar(30) NOT NULL,
  `email` varchar(50) NOT NULL,
  `tel` int DEFAULT NULL,
  `password` varchar(120) NOT NULL,
  `Drill_id` int DEFAULT NULL,
  `role` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `participant`
--

INSERT INTO `participant` (`id`, `firstname`, `lastname`, `email`, `tel`, `password`, `Drill_id`, `role`) VALUES
(1, 'Khalil', 'Karboul', 'khalil@gmail.com', 25141006, 'khalil', 3, 'participant'),
(2, 'Anas', 'Zribi', 'anas@gmail.com', 61616516, 'anas', 2, 'participant'),
(3, 'Soumaya', 'test1', 'soumaya@gmail.com', 88888888, 'soumaya', 3, 'participant'),
(4, 'test2', 'test2', 'test2@gmail.com', 3996556, 'tirst2', 4, 'participant'),
(5, 'salem', 'karoui', 'salem@gmail.com', 55621754, '12301230', 4, 'participant'),
(6, 'Khalil', 'Zribi', 'test11@gmail.com', 23232323, 'khalil22', 2, 'participant'),
(7, 'yesser', 'yesser', 'yesser@gmail.com', 91919191, 'yesser', 5, 'participant');

-- --------------------------------------------------------

--
-- Table structure for table `root`
--

CREATE TABLE `root` (
  `id` int NOT NULL,
  `email` varchar(50) NOT NULL,
  `password` varchar(120) NOT NULL,
  `role` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `root`
--

INSERT INTO `root` (`id`, `email`, `password`, `role`) VALUES
(1, 'root@gmail.com', 'root', 'root');

-- --------------------------------------------------------

--
-- Table structure for table `trainer`
--

CREATE TABLE `trainer` (
  `id` int NOT NULL,
  `firstname` varchar(30) NOT NULL,
  `lastname` varchar(30) NOT NULL,
  `email` varchar(50) NOT NULL,
  `tel` int DEFAULT NULL,
  `password` varchar(120) NOT NULL,
  `role` varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `trainer`
--

INSERT INTO `trainer` (`id`, `firstname`, `lastname`, `email`, `tel`, `password`, `role`) VALUES
(1, 'Akram', 'Allani', 'akram@gmail.com', 99999999, 'akram', 'trainer'),
(2, 'Ramzi ', 'Sassi', 'ramzi@gmail.com', 1616512, 'ramzi', 'trainer'),
(3, 'yesser', 'yesser', 'yesser@gmail.com', 5515191, 'yesser', 'trainer');

-- --------------------------------------------------------

--
-- Table structure for table `training`
--

CREATE TABLE `training` (
  `id` int DEFAULT NULL,
  `name` varchar(20) NOT NULL,
  `description` varchar(500) DEFAULT NULL,
  `period_in_days` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Dumping data for table `training`
--

INSERT INTO `training` (`id`, `name`, `description`, `period_in_days`) VALUES
(NULL, 'CEH', 'Hacking', 7),
(NULL, 'Cisco', 'desciption', 21),
(NULL, 'NSE4', 'desciption', 14);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `drill`
--
ALTER TABLE `drill`
  ADD PRIMARY KEY (`id`),
  ADD KEY `training_name` (`training_name`),
  ADD KEY `trainer_id` (`trainer_id`);

--
-- Indexes for table `participant`
--
ALTER TABLE `participant`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `password` (`password`),
  ADD UNIQUE KEY `tel` (`tel`),
  ADD KEY `Drill_id` (`Drill_id`);

--
-- Indexes for table `root`
--
ALTER TABLE `root`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `password` (`password`);

--
-- Indexes for table `trainer`
--
ALTER TABLE `trainer`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `password` (`password`),
  ADD UNIQUE KEY `tel` (`tel`);

--
-- Indexes for table `training`
--
ALTER TABLE `training`
  ADD PRIMARY KEY (`name`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `drill`
--
ALTER TABLE `drill`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `participant`
--
ALTER TABLE `participant`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `root`
--
ALTER TABLE `root`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `trainer`
--
ALTER TABLE `trainer`
  MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `drill`
--
ALTER TABLE `drill`
  ADD CONSTRAINT `drill_ibfk_1` FOREIGN KEY (`training_name`) REFERENCES `training` (`name`),
  ADD CONSTRAINT `drill_ibfk_2` FOREIGN KEY (`trainer_id`) REFERENCES `trainer` (`id`);

--
-- Constraints for table `participant`
--
ALTER TABLE `participant`
  ADD CONSTRAINT `participant_ibfk_1` FOREIGN KEY (`Drill_id`) REFERENCES `drill` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
