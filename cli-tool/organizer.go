package main

import (
	"flag"
	"fmt"
	"io/fs"
	"log"
	"os"
	"path/filepath"
)

func main() {
	sourceDir := flag.String("source", ".", "Source directory to organize")
	dryRun := flag.Bool("dry-run", false, "Simulate organizing files without moving them")
	flag.Parse()

	if *dryRun {
		fmt.Println("--- DRY RUN MODE ---")
	}

	err := organizeFiles(*sourceDir, *dryRun)
	if err != nil {
		log.Fatalf("Error organizing files: %v", err)
	}

	fmt.Println("Organization complete.")
}

func organizeFiles(root string, dryRun bool) error {
	return filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}

		if d.IsDir() || path == root {
			return nil
		}
		
		relPath, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		
		if filepath.Dir(relPath) != "." {
			return nil
		}

		ext := filepath.Ext(path)
		if ext == "" {
			ext = ".other"
		}

		dirName := ext[1:]
		if dirName == "other" {
			dirName = "other"
		}

		targetDir := filepath.Join(root, dirName)
		targetPath := filepath.Join(targetDir, d.Name())

		if dryRun {
			fmt.Printf("[DRY RUN] Would move %s to %s\n", path, targetPath)
			return nil
		}

		err = os.MkdirAll(targetDir, 0755)
		if err != nil {
			return err
		}

		fmt.Printf("Moving %s to %s\n", path, targetPath)
		return os.Rename(path, targetPath)
	})
}