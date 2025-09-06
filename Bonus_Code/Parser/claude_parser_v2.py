#!/usr/bin/env python3
"""
Claude Conversation Parser V2
Versione semplificata che gestisce meglio i turni vuoti

Author: Russo Davide (The DaveEloper)
Email: vibecoding@pcok.it
Project: ChatTokener Suite
Component: Claude Conversation Parser
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import argparse


class ClaudeConversationParser:
    def __init__(self, input_path: str, output_dir: str = None, base_folder: str = "Python"):
        self.input_path = Path(input_path)
        self.output_dir = output_dir  # Può essere None per usare la directory del progetto
        self.base_folder = base_folder
        self.conversation_counter = {}
        self.name_mappings = self.load_name_mappings()
    
    def load_name_mappings(self) -> Dict[str, str]:
        """Carica le mappature dei nomi dal file json_name_match.txt"""
        mappings = {}
        
        # Determina il percorso del file di mappatura
        if self.input_path.is_dir():
            mapping_file = self.input_path / "json_name_match.txt"
        else:
            mapping_file = self.input_path.parent / "json_name_match.txt"
        
        if mapping_file.exists():
            print(f"Trovato file di mappatura: {mapping_file}")
            with open(mapping_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line:
                        # Parsing della riga: uuid=Nome Conversazione
                        uuid, name = line.split('=', 1)
                        uuid = uuid.strip()
                        name = name.strip().strip('"')  # Rimuovi eventuali virgolette
                        mappings[uuid] = name
                        print(f"Mappatura trovata: {uuid} -> {name}")
        
        return mappings
        
    def parse_jsonl_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Legge un file JSONL e restituisce una lista di oggetti JSON"""
        messages = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        messages.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Errore nel parsing della riga: {e}")
        return messages
    
    def extract_project_name(self, cwd: str) -> str:
        """Estrae il nome del progetto dal percorso di lavoro"""
        if cwd and cwd != 'Unknown':
            path = Path(cwd)
            return path.name.replace(' ', '_')
        return "unknown_project"
    
    def generate_filename(self, messages: List[Dict[str, Any]], original_filename: str, file_path: Path) -> str:
        """Genera un nome file nel formato SpecStory"""
        if not messages:
            return original_filename + '.md'
        
        # Ottieni sempre il primo messaggio per avere accesso a cwd
        first_msg = messages[0] if messages else {}
        
        # Usa la data di creazione del file JSONL invece del timestamp interno
        try:
            # Su macOS, st_birthtime contiene la data di creazione
            creation_time = os.stat(file_path).st_birthtime
            dt = datetime.fromtimestamp(creation_time)
            date_prefix = dt.strftime("%Y-%m-%d_%H-%M")
            print(f"Debug: Usando data di creazione del file: {date_prefix}")
        except AttributeError:
            # Su sistemi non-macOS, usa st_ctime come fallback
            creation_time = os.stat(file_path).st_ctime
            dt = datetime.fromtimestamp(creation_time)
            date_prefix = dt.strftime("%Y-%m-%d_%H-%M")
            print(f"Debug: Usando ctime come fallback: {date_prefix}")
        except:
            # Se tutto fallisce, usa il timestamp del primo messaggio
            timestamp = first_msg.get('timestamp', '')
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_prefix = dt.strftime("%Y-%m-%d_%H-%M")
                print(f"Debug: Usando timestamp del messaggio come ultimo fallback: {date_prefix}")
            except:
                date_prefix = datetime.now().strftime("%Y-%m-%d_%H-%M")
                print(f"Debug: Usando data corrente come ultimo fallback: {date_prefix}")
        
        # Controlla se esiste una mappatura per questo file
        file_uuid = file_path.stem  # Estrai UUID senza estensione
        if file_uuid in self.name_mappings:
            # Usa il nome mappato
            custom_name = self.name_mappings[file_uuid]
            # Sostituisci spazi e underscore con trattini
            custom_name = custom_name.replace(' ', '-').replace('_', '-').lower()
            # Rimuovi caratteri non validi per i nomi file
            custom_name = ''.join(c for c in custom_name if c.isalnum() or c == '-')
            
            # Genera il nome finale senza il nome del progetto
            filename = f"{date_prefix}-{custom_name}.md"
            print(f"Usando nome personalizzato: {filename}")
        else:
            # Fallback: usa il nome del progetto come prima
            cwd = first_msg.get('cwd', 'Unknown')
            project_name = self.extract_project_name(cwd).lower()
            
            # Gestisci il contatore per conversazioni multiple
            if project_name not in self.conversation_counter:
                self.conversation_counter[project_name] = 0
            self.conversation_counter[project_name] += 1
            
            # Genera il nome finale
            filename = f"{date_prefix}-{project_name}_{self.conversation_counter[project_name]}.md"
        
        return filename
    
    def extract_text_content(self, content: Any) -> str:
        """Estrae il contenuto testuale da diversi formati di messaggio"""
        if isinstance(content, list):
            text_parts = []
            
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        text = item.get('text', '').strip()
                        if text:
                            text_parts.append(text)
                    elif item.get('type') == 'tool_use':
                        # Formatta i tool use
                        tool_name = item.get('name', 'Unknown Tool')
                        tool_input = item.get('input', {})
                        
                        if tool_name == 'Read':
                            file_path = tool_input.get('file_path', 'Unknown file')
                            text_parts.append(f"Read file: {file_path}")
                        elif tool_name == 'Write' or tool_name == 'Edit':
                            file_path = tool_input.get('file_path', 'Unknown file')
                            text_parts.append(f"{tool_name} file: {file_path}")
                        elif tool_name == 'LS':
                            path = tool_input.get('path', 'Unknown path')
                            text_parts.append(f"<details>\n            <summary>Listed directory {path}</summary>\n        \n(Directory listing will appear here)\n\n</details>")
                        else:
                            # Per altri tool, usa un formato generico
                            text_parts.append(f"{tool_name}: {json.dumps(tool_input, indent=2)}")
            
            return '\n\n'.join(text_parts) if text_parts else ''
        elif isinstance(content, str):
            return content
        else:
            return str(content)
    
    def convert_to_markdown(self, messages: List[Dict[str, Any]], source_filename: str = "") -> str:
        """Converte i messaggi in formato markdown compatibile con SpecStory"""
        markdown_lines = []
        
        # Header SpecStory
        markdown_lines.append("<!-- Generated by SpecStory -->")
        markdown_lines.append("")
        
        # Aggiungi il nome del file sorgente se disponibile
        if source_filename:
            markdown_lines.append(f"Source: {source_filename}")
            markdown_lines.append("")
        
        # Titolo con timestamp dal primo messaggio
        if messages:
            first_timestamp = messages[0].get('timestamp', '')
            try:
                dt = datetime.fromisoformat(first_timestamp.replace('Z', '+00:00'))
                formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                formatted_date = "Unknown Date"
            
            # Usa il nome della directory di lavoro come titolo
            cwd = messages[0].get('cwd', 'Unknown')
            project_name = Path(cwd).name.replace(' ', '_')
            
            markdown_lines.append(f"# {project_name} ({formatted_date})")
            markdown_lines.append("")
        
        # Raggruppa i messaggi in turni
        turns = []
        current_turn = {'user': None, 'assistant_messages': [], 'tool_results': []}
        
        for msg in messages:
            msg_type = msg.get('type', 'unknown')
            
            if msg_type == 'user':
                # Controlla se è un tool result
                if 'toolUseResult' in msg:
                    # È un tool result, aggiungilo al turno corrente senza creare un nuovo turno
                    current_turn['tool_results'].append(msg['toolUseResult'])
                else:
                    # È un vero messaggio user, quindi inizia un nuovo turno
                    if current_turn['user'] is not None or len(current_turn['assistant_messages']) > 0:
                        turns.append(current_turn)
                        current_turn = {'user': None, 'assistant_messages': [], 'tool_results': []}
                    current_turn['user'] = msg
                    
            elif msg_type == 'assistant':
                # Aggiungi TUTTI i messaggi dell'assistente (possono essere multipli)
                current_turn['assistant_messages'].append(msg)
        
        # Salva l'ultimo turno
        if current_turn['user'] is not None or len(current_turn['assistant_messages']) > 0:
            turns.append(current_turn)
        
        # Converti i turni in markdown
        for turn in turns:
            # Estrai contenuto user
            user_content = ""
            if turn['user'] and 'message' in turn['user'] and 'content' in turn['user']['message']:
                user_content = self.extract_text_content(turn['user']['message']['content'])
            
            # Estrai contenuto assistant (può essere multiplo)
            assistant_content_parts = []
            for assistant_msg in turn['assistant_messages']:
                if 'message' in assistant_msg and 'content' in assistant_msg['message']:
                    content = self.extract_text_content(assistant_msg['message']['content'])
                    if content.strip():
                        assistant_content_parts.append(content)
            
            assistant_content = '\n\n'.join(assistant_content_parts)
            
            # Controlla se è un turno di exit (da ignorare)
            is_exit_turn = False
            if user_content.strip():
                # Controlla pattern di exit
                if ('<command-name>exit</command-name>' in user_content or
                    '<local-command-stdout>(no content)</local-command-stdout>' in user_content):
                    is_exit_turn = True
            
            # Salta turni di exit
            if is_exit_turn:
                continue
            
            # Decidi se includere questo turno
            # Salta turni dove user è vuoto E assistant ha solo tool reference
            if not user_content.strip() and assistant_content.strip():
                # Controlla se l'assistant ha solo tool reference
                lines = assistant_content.strip().split('\n')
                has_real_content = False
                for line in lines:
                    line_stripped = line.strip()
                    # Ignora linee vuote, separatori e JSON
                    if not line_stripped or line_stripped in ['---', '{', '}', '[', ']']:
                        continue
                    
                    # Lista estesa di pattern che indicano solo tool reference o JSON
                    tool_patterns = [
                        'Edit file:', 'Write file:', 'Read file:', 'TodoWrite:', 
                        'Bash:', 'Task:', 'Grep:', 'Glob:', 'MultiEdit:', 'LS:',
                        '<details>', '</details>', '"todos":', '"id":', '"content":', 
                        '"status":', '"priority":', '"command":', '"description":',
                        '"prompt":', '"file_path":', '"edits":', '"old_string":',
                        '"new_string":', '"path":', '"pattern":', '```'
                    ]
                    
                    # Se la linea non inizia con un pattern noto E non è solo JSON
                    is_tool_or_json = any(p in line_stripped for p in tool_patterns)
                    is_json_line = line_stripped.startswith('"') and line_stripped.endswith(('",', '":'))
                    
                    if not is_tool_or_json and not is_json_line:
                        has_real_content = True
                        break
                
                if not has_real_content:
                    # Salta questo turno completamente
                    continue
            
            # Aggiungi il turno
            markdown_lines.append("_**User**_")
            markdown_lines.append("")
            markdown_lines.append(user_content)
            markdown_lines.append("")
            markdown_lines.append("---")
            markdown_lines.append("")
            markdown_lines.append("_**Assistant**_")
            markdown_lines.append("")
            
            if assistant_content.strip():
                markdown_lines.append(assistant_content)
            
            # Aggiungi tool results
            for result in turn['tool_results']:
                if isinstance(result, dict):
                    if 'stdout' in result and result['stdout']:
                        markdown_lines.append("")
                        markdown_lines.append("```")
                        markdown_lines.append(result['stdout'])
                        markdown_lines.append("```")
                    if 'stderr' in result and result['stderr']:
                        markdown_lines.append("")
                        markdown_lines.append("**Error:**")
                        markdown_lines.append("```")
                        markdown_lines.append(result['stderr'])
                        markdown_lines.append("```")
                elif isinstance(result, str) and result.strip():
                    markdown_lines.append("")
                    markdown_lines.append("```")
                    markdown_lines.append(result)
                    markdown_lines.append("```")
            
            markdown_lines.append("")
            markdown_lines.append("---")
            markdown_lines.append("")
        
        return '\n'.join(markdown_lines)
    
    def clean_fake_turns(self, markdown_content: str) -> str:
        """Seconda passata per rimuovere turni fake dal markdown generato"""
        lines = markdown_content.split('\n')
        cleaned_lines = []
        i = 0
        
        while i < len(lines):
            # Pattern per identificare un turno fake:
            # _**User**_
            # [linee vuote]
            # ---
            # [linee vuote]
            # _**Assistant**_
            
            if (i < len(lines) and lines[i].strip() == '_**User**_'):
                # Salva la posizione iniziale
                start_i = i
                i += 1
                
                # Salta linee vuote dopo User
                while i < len(lines) and lines[i].strip() == '':
                    i += 1
                
                # Se troviamo --- dopo user vuoto
                if i < len(lines) and lines[i].strip() == '---':
                    i += 1
                    
                    # Salta linee vuote dopo ---
                    while i < len(lines) and lines[i].strip() == '':
                        i += 1
                    
                    # Se troviamo _**Assistant**_ subito dopo, è un turno fake
                    if i < len(lines) and lines[i].strip() == '_**Assistant**_':
                        # Questo è un turno fake! Saltiamo tutto fino al prossimo ---
                        while i < len(lines) and lines[i].strip() != '---':
                            i += 1
                        
                        # Salta anche il --- finale e le linee vuote
                        if i < len(lines) and lines[i].strip() == '---':
                            i += 1
                            while i < len(lines) and lines[i].strip() == '':
                                i += 1
                        
                        # Continua senza aggiungere nulla a cleaned_lines
                        continue
                    else:
                        # Non è un fake turn, ripristina e aggiungi normalmente
                        for j in range(start_i, i):
                            cleaned_lines.append(lines[j])
                else:
                    # Non è il pattern che cerchiamo, aggiungi tutto
                    for j in range(start_i, i):
                        cleaned_lines.append(lines[j])
            else:
                # Linea normale, aggiungila
                cleaned_lines.append(lines[i])
                i += 1
        
        # Rimuovi linee vuote multiple consecutive alla fine
        while cleaned_lines and cleaned_lines[-1].strip() == '':
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def get_project_path_from_cwd(self, cwd: str) -> Optional[Path]:
        """Estrae il percorso del progetto dal cwd"""
        if not cwd or cwd == 'Unknown':
            return None
        return Path(cwd)
    
    def get_project_path_from_jsonl_path(self, jsonl_path: Path) -> Optional[Path]:
        """Estrae il percorso del progetto dal path del file JSONL"""
        # Se il file è in .claude/projects/, decodifica il nome della cartella
        if '.claude/projects/' in str(jsonl_path):
            # Estrai il nome della cartella del progetto
            project_folder = jsonl_path.parent.name
            # Converti da -Users-daviderusso-Documents-Programming-Python-Claude-Conversation-Parser
            # a /Users/daviderusso/Documents/Programming/Python/Claude_Conversation_Parser
            if project_folder.startswith('-'):
                # Dividi per trovare le parti del percorso
                parts = project_folder[1:].split('-')
                
                # Ricostruisci il percorso considerando che l'ultima parte potrebbe avere trattini
                # Assumiamo che i primi elementi fino a "Python" siano parti del path
                path_parts = []
                project_parts = []
                found_base = False
                
                for i, part in enumerate(parts):
                    if not found_base:
                        path_parts.append(part)
                        if part == self.base_folder:
                            found_base = True
                    else:
                        # Tutto dopo la base folder è il nome del progetto
                        project_parts = parts[i:]
                        break
                
                # Ricostruisci il percorso
                if project_parts:
                    project_name = '_'.join(project_parts)  # Usa underscore per il nome del progetto
                    full_path = '/' + '/'.join(path_parts) + '/' + project_name
                    return Path(full_path)
                
        return None
    
    def process_file(self, file_path: Path) -> None:
        """Processa un singolo file JSONL"""
        print(f"Processing: {file_path}")
        
        messages = self.parse_jsonl_file(file_path)
        if not messages:
            print(f"Nessun messaggio trovato in {file_path}")
            return
        
        # Passa anche il nome del file sorgente
        markdown_content = self.convert_to_markdown(messages, file_path.name)
        
        # Seconda passata per rimuovere turni fake
        cleaned_content = self.clean_fake_turns(markdown_content)
        
        # Genera il nome del file nel formato SpecStory
        output_filename = self.generate_filename(messages, file_path.stem, file_path)
        
        # Determina la directory di output
        if self.output_dir:
            # Usa la directory specificata dall'utente
            output_dir = Path(self.output_dir)
            output_dir.mkdir(exist_ok=True)
        else:
            # Prima prova a estrarre il percorso dal nome della cartella JSONL
            project_path = self.get_project_path_from_jsonl_path(file_path)
            print(f"Debug: Percorso estratto dal JSONL path: {project_path}")
            
            # Se non funziona, prova con il cwd dal JSON
            if not project_path or not project_path.exists():
                if messages and 'cwd' in messages[0]:
                    cwd = messages[0]['cwd']
                    print(f"Debug: CWD dal JSON: {cwd}")
                    project_path = self.get_project_path_from_cwd(cwd)
            
            if project_path and project_path.exists():
                # Crea la struttura .specstory/history nel progetto
                output_dir = project_path / '.specstory' / 'history'
                output_dir.mkdir(parents=True, exist_ok=True)
                print(f"Salvando in: {output_dir}")
            else:
                # Fallback alla directory di output di default
                output_dir = Path('output')
                output_dir.mkdir(exist_ok=True)
                print(f"Warning: Impossibile determinare il percorso del progetto, uso directory di default")
                if project_path:
                    print(f"Debug: Il percorso {project_path} non esiste")
        
        output_path = output_dir / output_filename
        
        # Scrivi il file markdown pulito
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        # Conta i turni prima e dopo la pulizia per debug
        turns_before = markdown_content.count('_**User**_')
        turns_after = cleaned_content.count('_**User**_')
        
        print(f"Output salvato in: {output_path}")
        print(f"Turni ridotti da {turns_before} a {turns_after} dopo la seconda pulizia")
    
    def process_directory(self) -> None:
        """Processa tutti i file JSONL nella directory di input"""
        if self.input_path.is_file():
            self.process_file(self.input_path)
        elif self.input_path.is_dir():
            jsonl_files = list(self.input_path.glob('*.jsonl'))
            if not jsonl_files:
                print(f"Nessun file JSONL trovato in {self.input_path}")
                return
            
            for file_path in jsonl_files:
                self.process_file(file_path)
        else:
            print(f"Path non valido: {self.input_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Converte le conversazioni Claude Code da JSONL a Markdown (V2)'
    )
    parser.add_argument(
        'input_path',
        help='Path al file JSONL o alla directory contenente i file JSONL'
    )
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='Directory di output per i file markdown (default: .specstory/history del progetto)'
    )
    parser.add_argument(
        '-b', '--base-folder',
        default='Python',
        help='Nome della cartella base per identificare i progetti (default: Python)'
    )
    
    args = parser.parse_args()
    
    # Crea il parser e processa i file
    conv_parser = ClaudeConversationParser(args.input_path, args.output, args.base_folder)
    conv_parser.process_directory()


if __name__ == '__main__':
    main()