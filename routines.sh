#!/bin/bash

# Legacy routine workflow wrapper
# Prefer ./hevy.sh for the umbrella Hevy toolkit CLI

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Detect Python command
if [ -x ".venv/Scripts/python.exe" ]; then
    PYTHON=".venv/Scripts/python.exe"
elif [ -x "venv/bin/python3" ]; then
    PYTHON="venv/bin/python3"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
else
    PYTHON="python"
fi

# Display help
show_help() {
    cat << EOF
${BLUE}Legacy Routine Workflow Helper${NC}

Usage: ./routines.sh <command> [options]

Recommended umbrella entrypoint:
    ./hevy.sh routines <command> [options]

Commands:
  ${GREEN}validate <file|dir|pattern>${NC}     Validate exercise IDs in routine JSON file(s)
  ${GREEN}upload <file|dir|pattern>${NC}        Upload routine(s) to Hevy API (with structure check)
  ${GREEN}batch-validate <dir>${NC}            Validate all JSON files in directory
  ${GREEN}batch-upload <dir>${NC}              Upload all validated JSON files in directory
  ${GREEN}interactive <file>${NC}              Validate with interactive mode (add missing exercises)
  ${GREEN}check <file>${NC}                    Check JSON structure BEFORE validation (catch API errors early)
  ${GREEN}list${NC}                            List all routine files in input/
  ${GREEN}help${NC}                            Show this help message

Examples:
  ./routines.sh validate input/dia_1_pecho_hombro_v2.json
  ./routines.sh check input/dia_3_pierna.json         (structure check before upload)
  ./routines.sh upload input/dia_3_pierna.json
  ./routines.sh batch-validate input/
  ./routines.sh batch-upload input/
  ./routines.sh interactive input/dia_4_biceps_triceps.json
  ./routines.sh validate "input/dia_{1,2,3}_*.json"

Options:
  --dry-run              Show what would be done without uploading
  --no-validate          Skip validation during upload
  --no-enhance           Skip warmup weight enhancement
  --warmup-strategy      Choose warmup strategy (recent|average|mode)

Resources:
  TEMPLATE_routine.json           Copy this to create new routines
  QUICK_START.md                  Quick reference for structure rules
  API_STRUCTURE_GUIDE.md          Detailed API requirements
  validate_structure.py           Check JSON structure for API errors

EOF
}

# Validate command
cmd_validate() {
    local target="$1"
    
    if [ -z "$target" ]; then
        echo -e "${RED}❌ Please specify a file, directory, or pattern${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔍 Validating: $target${NC}"
    "$PYTHON" exercise_validator.py "$target" -v
}

# Interactive validation command
cmd_interactive() {
    local target="$1"
    
    if [ -z "$target" ]; then
        echo -e "${RED}❌ Please specify a file${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔍 Validating (interactive mode): $target${NC}"
    "$PYTHON" exercise_validator.py "$target" -i
}

# Upload command
cmd_upload() {
    local target="$1"
    shift
    local extra_args="$@"
    
    if [ -z "$target" ]; then
        echo -e "${RED}❌ Please specify a file, directory, or pattern${NC}"
        exit 1
    fi
    
    # Pre-flight structure check
    echo -e "${BLUE}🔍 Pre-flight structure check...${NC}"
    if [ -f "$target" ]; then
        "$PYTHON" validate_structure.py "$target" || {
            echo -e "${RED}❌ Structure validation failed. Review errors above.${NC}"
            exit 1
        }
    fi
    
    echo -e "${BLUE}📤 Uploading: $target${NC}"
    "$PYTHON" routine_uploader.py "$target" $extra_args
}

# Batch validate command
cmd_batch_validate() {
    local dir="${1:-.}"
    
    if [ ! -d "$dir" ]; then
        echo -e "${RED}❌ Directory not found: $dir${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔍 Batch validating all routines in: $dir${NC}"
    count=0
    for file in "$dir"/*.json; do
        if [ -f "$file" ]; then
            count=$((count + 1))
            echo -e "\n${YELLOW}[$(printf "%02d" $count)]${NC} Validating: $(basename "$file")"
            "$PYTHON" exercise_validator.py "$file" -v || echo -e "${RED}  ⚠️  Validation failed${NC}"
        fi
    done
    
    if [ $count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  No JSON files found in $dir${NC}"
    fi
}

# Batch upload command
cmd_batch_upload() {
    local dir="${1:-.}"
    shift
    local extra_args="$@"
    
    if [ ! -d "$dir" ]; then
        echo -e "${RED}❌ Directory not found: $dir${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}📤 Batch uploading all routines in: $dir${NC}"
    "$PYTHON" routine_uploader.py "$dir" $extra_args
}

# List command
cmd_list() {
    if [ ! -d "input" ]; then
        echo -e "${RED}❌ input/ directory not found${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}📋 Available routines in input/:${NC}"
    local count=0
    for file in input/*.json; do
        if [ -f "$file" ]; then
            count=$((count + 1))
            filename=$(basename "$file")
            filesize=$(du -h "$file" | cut -f1)
            printf "  ${GREEN}%2d.${NC} %-35s (${filesize})\n" $count "$filename"
        fi
    done
    
    if [ $count -eq 0 ]; then
        echo -e "${YELLOW}  No routines found${NC}"
    else
        echo ""
        echo -e "  ${BLUE}Total: $count routines${NC}"
    fi
}

# Structure check command
cmd_check() {
    local target="$1"
    
    if [ -z "$target" ]; then
        echo -e "${RED}❌ Please specify a file${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔍 Checking JSON structure for API errors...${NC}"
    "$PYTHON" validate_structure.py "$target"
}

# Main command router
main() {
    local command="${1:---help}"
    shift || true
    
    case "$command" in
        validate)
            cmd_validate "$@"
            ;;
        upload)
            cmd_upload "$@"
            ;;
        interactive)
            cmd_interactive "$@"
            ;;
        batch-validate)
            cmd_batch_validate "$@"
            ;;
        batch-upload)
            cmd_batch_upload "$@"
            ;;
        check)
            cmd_check "$@"
            ;;
        list)
            cmd_list
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}❌ Unknown command: $command${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
