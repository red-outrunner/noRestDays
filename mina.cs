using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;

namespace DuplicateFileScanner
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("--- C# Duplicate File Scanner ---");
            Console.WriteLine("Enter the path to the directory you want to scan:");
            string directoryPath = Console.ReadLine();

            if (!Directory.Exists(directoryPath))
            {
                Console.WriteLine("Error: The specified directory does not exist.");
                return;
            }

            try
            {
                FindAndProcessDuplicates(directoryPath);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"An unexpected error occurred: {ex.Message}");
            }

            Console.WriteLine("\nScan complete. Press any key to exit.");
            Console.ReadKey();
        }

        /// <summary>
        /// Finds and processes duplicate files in the specified directory.
        /// </summary>
        /// <param name="directoryPath">The path to the directory to scan.</param>
        public static void FindAndProcessDuplicates(string directoryPath)
        {
            // Dictionary to store file hashes and the list of files with that hash.
            var hashes = new Dictionary<string, List<string>>();

            Console.WriteLine("\nScanning files and calculating hashes...");

            // Recursively get all files from the directory and its subdirectories.
            var files = Directory.EnumerateFiles(directoryPath, "*", SearchOption.AllDirectories);

            foreach (var filePath in files)
            {
                try
                {
                    // Calculate the hash of the file.
                    string fileHash = CalculateFileHash(filePath);

                    // If the hash already exists, add the file path to the list.
                    if (hashes.ContainsKey(fileHash))
                    {
                        hashes[fileHash].Add(filePath);
                    }
                    else // Otherwise, create a new entry.
                    {
                        hashes[fileHash] = new List<string> { filePath };
                    }
                }
                catch (IOException ex)
                {
                    Console.WriteLine($"Could not access file: {filePath}. Error: {ex.Message}");
                }
            }

            Console.WriteLine("Scan finished. Finding duplicates...");

            // Filter out the hashes that have more than one file (i.e., duplicates).
            var duplicates = hashes.Where(kvp => kvp.Value.Count > 1).ToList();

            if (!duplicates.Any())
            {
                Console.WriteLine("\nNo duplicate files found.");
                return;
            }

            Console.WriteLine($"\nFound {duplicates.Count} set(s) of duplicate files.");
            
            // Process each set of duplicate files.
            foreach (var duplicateSet in duplicates)
            {
                Console.WriteLine($"\n--- Duplicate Set (Hash: {duplicateSet.Key}) ---");
                List<string> filePaths = duplicateSet.Value;

                // We keep the first file as the "original" and process the rest.
                Console.WriteLine($"Keeping: {filePaths[0]}");

                for (int i = 1; i < filePaths.Count; i++)
                {
                    ProcessDuplicateFile(filePaths[i]);
                }
            }
        }

        /// <summary>
        /// Provides options to the user for handling a duplicate file.
        /// </summary>
        /// <param name="filePath">The path of the duplicate file.</param>
        private static void ProcessDuplicateFile(string filePath)
        {
            Console.WriteLine($"  -> Found duplicate: {filePath}");
            
            while (true)
            {
                Console.Write("  Choose an action: (D)elete, (R)ename, (S)kip: ");
                string choice = Console.ReadLine()?.ToUpper();

                switch (choice)
                {
                    case "D":
                        DeleteFile(filePath);
                        return; // Action complete, exit loop
                    case "R":
                        if (RenameFile(filePath))
                        {
                           return; // Action complete, exit loop
                        }
                        // if rename fails, loop again for a new choice
                        break;
                    case "S":
                        Console.WriteLine($"  Skipped: {filePath}");
                        return; // Action complete, exit loop
                    default:
                        Console.WriteLine("  Invalid choice. Please try again.");
                        break;
                }
            }
        }
        
        /// <summary>
        /// Deletes the specified file.
        /// </summary>
        /// <param name="filePath">Path to the file to delete.</param>
        private static void DeleteFile(string filePath)
        {
            try
            {
                File.Delete(filePath);
                Console.WriteLine($"  Deleted: {filePath}");
            }
            catch (IOException ex)
            {
                Console.WriteLine($"  Error deleting file: {ex.Message}");
            }
        }

        /// <summary>
        /// Renames the specified file based on user input.
        /// </summary>
        /// <param name="filePath">Path to the file to rename.</param>
        /// <returns>True if rename was successful, false otherwise.</returns>
        private static bool RenameFile(string filePath)
        {
            Console.Write("  Enter new file name (with extension): ");
            string newName = Console.ReadLine();

            if (string.IsNullOrWhiteSpace(newName))
            {
                Console.WriteLine("  Invalid new name. Aborting rename.");
                return false;
            }

            try
            {
                string directory = Path.GetDirectoryName(filePath);
                string newFilePath = Path.Combine(directory, newName);

                if (File.Exists(newFilePath))
                {
                    Console.WriteLine($"  A file with the name '{newName}' already exists in this directory. Please choose a different name.");
                    return false;
                }
                
                File.Move(filePath, newFilePath);
                Console.WriteLine($"  Renamed: {filePath} -> {newFilePath}");
                return true;
            }
            catch (IOException ex)
            {
                Console.WriteLine($"  Error renaming file: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Calculates the SHA256 hash for a given file.
        /// </summary>
        /// <param name="filePath">The path to the file.</param>
        /// <returns>A string representing the file's hash.</returns>
        private static string CalculateFileHash(string filePath)
        {
            using (var sha256 = SHA256.Create())
            {
                using (var stream = File.OpenRead(filePath))
                {
                    byte[] hashBytes = sha256.ComputeHash(stream);
                    // Convert byte array to a string
                    StringBuilder sb = new StringBuilder();
                    foreach (byte b in hashBytes)
                    {
                        sb.Append(b.ToString("x2"));
                    }
                    return sb.ToString();
                }
            }
        }
    }
}
