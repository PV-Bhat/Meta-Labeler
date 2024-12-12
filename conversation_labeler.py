import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Canvas, Scrollbar
import json
import pandas as pd
from pathlib import Path
import os
import threading
import time

# Ensure you have the required packages installed:
# pip install pandas openpyxl

print("Current Working Directory:", os.getcwd())
print("Python Version:", os.sys.version)

class ConversationLabeler:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversation Labeler")
        self.root.geometry("1600x800")  # Increased width to accommodate new layout

        # Data storage
        self.current_file_index = 0
        self.json_files = []
        self.current_data = None
        self.output_file = "labeled_conversations.xlsx"

        # Initialize the DataFrame for storing labels if it doesn't exist
        if not Path(self.output_file).exists():
            self.df = pd.DataFrame(columns=[
                'conversation_id', 'segment', 'sentiment', 'engagement_score',
                'customer_effort_score', 'response_type', 'comments',
                'message_sent_length', 'message_received_length', 'total_messages'
            ])
            self.df.to_excel(self.output_file, index=False)
        else:
            self.df = pd.read_excel(self.output_file)

        # Store colors for different segments
        self.segment_colors = {
            'Intake': '#FFCCCC',      # Light Red
            'Engaged': '#FFFF99',     # Light Yellow
            'Qualified': '#CCFFCC'    # Light Green
        }

        # Dictionary to hold segment frames and their widgets
        self.segment_vars = {}

        # Define segments
        self.segments = ['Intake', 'Engaged', 'Qualified']

        # Dictionary to map senders to colors
        self.sender_colors = {}
        self.next_color_index = 0
        self.available_colors = [
            '#ADD8E6',  # Light Blue
            '#90EE90',  # Light Green
            '#FFA07A',  # Light Salmon
            '#FFD700',  # Gold
            '#DDA0DD',  # Plum
            '#FFB6C1',  # Light Pink
            '#20B2AA',  # Light Sea Green
            '#87CEFA',  # Light Sky Blue
            '#F08080',  # Light Coral
            '#9370DB'   # Medium Purple
        ]

        self.setup_ui()
        self.load_json_files()
        self.bind_keys()

    def setup_ui(self):
        # Apply a modern theme and font
        style = ttk.Style(self.root)
        style.theme_use('clam')

        # Create main panels
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_panel = tk.Frame(main_frame, bg='white')
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_panel = tk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.Y)

        explanation_panel = tk.Frame(main_frame, bg='white')
        explanation_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Conversation Display (Left Panel)
        tk.Label(left_panel, text="Conversation", font=('Segoe UI', 16, 'bold'), bg='white').pack(anchor=tk.W, padx=10, pady=10)
        self.conversation_text = scrolledtext.ScrolledText(left_panel, wrap=tk.WORD, width=60, state='disabled', font=('Segoe UI', 10), bg='#F5F5F5')
        self.conversation_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Labeling Controls (Right Panel)
        segmentation_frame = ttk.LabelFrame(right_panel, text="Segmentation Control")
        segmentation_frame.pack(fill="x", padx=10, pady=10)

        self.segment_mode_var = tk.IntVar(value=3)  # Default to all segments enabled

        ttk.Label(segmentation_frame, text="Select Segments to Label:", font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=(0, 5))

        modes = [
            ("Label Intake Only", 1),
            ("Label Intake and Engaged", 2),
            ("Label All Segments", 3)
        ]

        for idx, (text, mode) in enumerate(modes):
            rb = ttk.Radiobutton(segmentation_frame, text=text, variable=self.segment_mode_var, value=mode, command=self.update_active_segments)
            rb.pack(anchor="w", pady=1)  # Reduced pady

        # Create separate sections for each segment
        self.create_segment_frames(right_panel)

        # Navigation Buttons with Emojis
        button_frame = tk.Frame(right_panel)
        button_frame.pack(fill="x", pady=10)  # Reduced pady

        # Change the order of buttons as per user request
        # New order: Save & Next, Save, Skip
        tk.Button(button_frame, text="💾➡️ Save & Next", command=self.save_and_next, font=('Segoe UI', 12), width=15).pack(side=tk.LEFT, padx=5, pady=2)  # Reduced pady
        tk.Button(button_frame, text="💾 Save", command=self.save_current, font=('Segoe UI', 12), width=15).pack(side=tk.LEFT, padx=5, pady=2)
        tk.Button(button_frame, text="⏭️ Skip", command=self.skip_current, font=('Segoe UI', 12), width=15).pack(side=tk.LEFT, padx=5, pady=2)

        # Progress Label
        self.progress_var = tk.StringVar(value="Conversation 0/0")
        tk.Label(right_panel, textvariable=self.progress_var, font=('Segoe UI', 12, 'bold')).pack(pady=5)  # Reduced pady

        # Progress Bar
        self.progress_bar = ttk.Progressbar(right_panel, orient='horizontal', length=200, mode='determinate')
        self.progress_bar.pack(pady=2)  # Reduced pady
        self.update_progress_bar()

        # Explanations Panel (Rightmost Panel)
        self.create_explanations_panel(explanation_panel)

        # Notification Label (Transient)
        self.notification_label = tk.Label(main_frame, text="", font=('Segoe UI', 10, 'bold'), bg='#D3D3D3', fg='black')
        self.notification_label.place(relx=0.5, rely=0.05, anchor='n')  # Position at top center

    def create_explanations_panel(self, parent):
        """
        Creates the explanations panel on the right side.
        """
        tk.Label(parent, text="Segment Definitions", font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=5)

        # Segment Definitions
        segment_definitions_frame = tk.Frame(parent, bg='white')
        segment_definitions_frame.pack(fill="x", padx=5, pady=2)  # Reduced padding
        definitions_text = (
            "• **Intake**: Initial stage with basic user interactions.\n"
            "• **Engaged**: Active user interactions and follow-up questions.\n"
            "• **Qualified**: User shows strong interest or readiness to proceed."
        )
        tk.Label(segment_definitions_frame, text=definitions_text, bg='white', font=('Segoe UI', 10), justify='left').pack(anchor='w')

        tk.Label(parent, text="Metric Explanations", font=('Segoe UI', 14, 'bold'), bg='white').pack(pady=5)

        # Sentiment Explanation
        sentiment_explanation_frame = tk.Frame(parent, bg='white')
        sentiment_explanation_frame.pack(fill="x", padx=5, pady=2)  # Reduced padding
        tk.Label(sentiment_explanation_frame, text="Sentiment Score:", font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')
        sentiment_text = (
            "1: Very Negative\n"
            "2: Negative\n"
            "3: Neutral\n"
            "4: Positive\n"
            "5: Very Positive"
        )
        tk.Label(sentiment_explanation_frame, text=sentiment_text, bg='white', font=('Segoe UI', 10), justify='left').pack(anchor='w')

        # Engagement Explanation
        engagement_explanation_frame = tk.Frame(parent, bg='white')
        engagement_explanation_frame.pack(fill="x", padx=5, pady=2)  # Reduced padding
        tk.Label(engagement_explanation_frame, text="Engagement Score:", font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')
        engagement_text = (
            "1: Minimal engagement\n"
            "2: Low engagement\n"
            "3: Moderate engagement\n"
            "4: High engagement\n"
            "5: Very high engagement"
        )
        tk.Label(engagement_explanation_frame, text=engagement_text, bg='white', font=('Segoe UI', 10), justify='left').pack(anchor='w')

        # CES Explanation
        ces_explanation_frame = tk.Frame(parent, bg='white')
        ces_explanation_frame.pack(fill="x", padx=5, pady=2)  # Reduced padding
        tk.Label(ces_explanation_frame, text="Customer Effort Score (CES):", font=('Segoe UI', 12, 'bold'), bg='white').pack(anchor='w')
        ces_text = (
            "1: Very Low Effort\n"
            "2: Low Effort\n"
            "3: Neutral Effort\n"
            "4: High Effort\n"
            "5: Very High Effort"
        )
        tk.Label(ces_explanation_frame, text=ces_text, bg='white', font=('Segoe UI', 10), justify='left').pack(anchor='w')

    def bind_keys(self):
        """
        Bind specific keys to actions:
        - Enter: Save & Next
        - '0': Save
        - '9': Skip (with confirmation)
        """
        self.root.bind('<Return>', lambda event: self.save_and_next())
        self.root.bind('<Key-0>', lambda event: self.save_current())
        self.root.bind('<Key-9>', lambda event: self.skip_current())

    def create_segment_frames(self, parent):
        """
        Creates frames for each segment in the user interface.
        """
        for idx, segment in enumerate(self.segments):
            frame = ttk.LabelFrame(parent, text=segment)
            frame.pack(fill="x", padx=10, pady=5)  # Reduced pady

            # Set the background color for the frame
            frame.configure(style=f"{segment}.TLabelframe")

            # Sentiment Score
            sentiment_frame = tk.Frame(frame, bg='#333333')  # Dark when unselected
            sentiment_frame.pack(anchor="w", pady=2, fill="x")  # Reduced pady
            tk.Label(sentiment_frame, text="Sentiment Score", bg='#333333', font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))

            sentiment_var = tk.IntVar(value=0)  # No default selection
            for i in range(1, 6):
                rb = tk.Radiobutton(sentiment_frame, text=str(i), variable=sentiment_var, value=i, bg='#333333', font=('Segoe UI', 10, 'bold'))
                rb.pack(side=tk.LEFT, padx=2)  # Align to the left
            self.segment_vars[f"{segment}_sentiment_var"] = sentiment_var

            # Add trace to update background
            def update_sentiment_bg(*args, seg=segment, var=sentiment_var, frame=sentiment_frame):
                if var.get() > 0:
                    frame.configure(bg=self.segment_colors[seg])
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label) or isinstance(widget, tk.Radiobutton):
                            widget.configure(bg=self.segment_colors[seg])
                else:
                    frame.configure(bg='#333333')
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label) or isinstance(widget, tk.Radiobutton):
                            widget.configure(bg='#333333')

            sentiment_var.trace_add("write", update_sentiment_bg)

            # Engagement Score
            engagement_frame = tk.Frame(frame, bg='#333333')
            engagement_frame.pack(anchor="w", pady=2, fill="x")  # Reduced pady
            tk.Label(engagement_frame, text="Engagement Score", bg='#333333', font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))

            engagement_var = tk.IntVar(value=0)  # No default selection
            for i in range(1, 6):
                rb = tk.Radiobutton(engagement_frame, text=str(i), variable=engagement_var, value=i, bg='#333333', font=('Segoe UI', 10, 'bold'))
                rb.pack(side=tk.LEFT, padx=2)
            self.segment_vars[f"{segment}_engagement_var"] = engagement_var

            def update_engagement_bg(*args, seg=segment, var=engagement_var, frame=engagement_frame):
                if var.get() > 0:
                    frame.configure(bg=self.segment_colors[seg])
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label) or isinstance(widget, tk.Radiobutton):
                            widget.configure(bg=self.segment_colors[seg])
                else:
                    frame.configure(bg='#333333')
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label) or isinstance(widget, tk.Radiobutton):
                            widget.configure(bg='#333333')

            engagement_var.trace_add("write", update_engagement_bg)

            # Customer Effort Score
            ces_frame = tk.Frame(frame, bg='#333333')
            ces_frame.pack(anchor="w", pady=2, fill="x")  # Reduced pady
            tk.Label(ces_frame, text="Customer Effort Score", bg='#333333', font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))

            ces_var = tk.IntVar(value=0)  # No default selection
            for i in range(5, 0, -1):  # From 5 to 1
                rb = tk.Radiobutton(ces_frame, text=str(i), variable=ces_var, value=i, bg='#333333', font=('Segoe UI', 10, 'bold'))
                rb.pack(side=tk.LEFT, padx=2)  # Align to the left
            self.segment_vars[f"{segment}_ces_var"] = ces_var

            def update_ces_bg(*args, seg=segment, var=ces_var, frame=ces_frame):
                if var.get() > 0:
                    frame.configure(bg=self.segment_colors[seg])
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label) or isinstance(widget, tk.Radiobutton):
                            widget.configure(bg=self.segment_colors[seg])
                else:
                    frame.configure(bg='#333333')
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label) or isinstance(widget, tk.Radiobutton):
                            widget.configure(bg='#333333')

            ces_var.trace_add("write", update_ces_bg)

            # Response Type (Radiobuttons aligned to the left)
            response_frame = tk.Frame(frame, bg='#333333')
            response_frame.pack(anchor="w", pady=2, fill="x")  # Reduced pady
            tk.Label(response_frame, text="Response Type", bg='#333333', font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
            response_type_var = tk.StringVar(value='')  # No default selection
            response_types = ["Manual", "Templated", "GPT"]
            for text in response_types:  # Keep the original order
                rb = tk.Radiobutton(response_frame, text=text, variable=response_type_var, value=text, bg='#333333', font=('Segoe UI', 10, 'bold'))
                rb.pack(side=tk.LEFT, padx=2)
            self.segment_vars[f"{segment}_response_type_var"] = response_type_var

            def update_response_type_bg(*args, seg=segment, var=response_type_var, frame=response_frame):
                if var.get() != '':
                    frame.configure(bg=self.segment_colors[seg])
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label) or isinstance(widget, tk.Radiobutton):
                            widget.configure(bg=self.segment_colors[seg])
                else:
                    frame.configure(bg='#333333')
                    for widget in frame.winfo_children():
                        if isinstance(widget, tk.Label) or isinstance(widget, tk.Radiobutton):
                            widget.configure(bg='#333333')

            response_type_var.trace_add("write", update_response_type_bg)

            # Store all widgets for enabling/disabling
            self.segment_vars[f"{segment}_widgets"] = {
                "frame": frame,
                "widgets_list": frame.winfo_children(),
            }

    def update_active_segments(self):
        """
        Enables or disables segment sections based on the selected segmentation mode.
        """
        mode = self.segment_mode_var.get()  # Get the selected mode from the radio buttons
        for idx, segment in enumerate(self.segments, start=1):  # Iterate through all segments
            widgets = self.segment_vars[f"{segment}_widgets"]
            if idx <= mode:  # Enable if the segment index is within the selected mode
                self.enable_segment(widgets)
            else:  # Disable if it's beyond the selected mode
                self.disable_segment(widgets)

    def enable_segment(self, widgets):
        """
        Enables all input widgets within a segment.
        """
        # Enable all widgets in the widgets_list
        for widget in widgets["widgets_list"]:
            # Enable Radiobuttons
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    child.configure(state="normal")
            else:
                widget.configure(state="normal")

    def disable_segment(self, widgets):
        """
        Disables all input widgets within a segment and resets their values.
        """
        # Disable all widgets in the widgets_list
        for widget in widgets["widgets_list"]:
            # Disable Radiobuttons
            if isinstance(widget, tk.Frame):
                for child in widget.winfo_children():
                    child.configure(state="disabled")
            else:
                widget.configure(state="disabled")
        # Reset all values for the disabled segment
        segment = widgets["frame"].cget("text")
        self.segment_vars[f"{segment}_sentiment_var"].set(0)  # Reset sentiment to no selection
        self.segment_vars[f"{segment}_engagement_var"].set(0)  # Reset engagement to no selection
        self.segment_vars[f"{segment}_ces_var"].set(0)  # Reset customer effort to no selection
        self.segment_vars[f"{segment}_response_type_var"].set("")  # Reset response type to no selection

    def load_json_files(self):
        """
        Loads all JSON files from the 'conversations' directory.
        """
        # Update the path to your 'conversations' directory
        json_path = Path(input('Please enter the path to your conversations directory: ') or r"Path to your conversations directory (e.g., './conversations')")
        print(f"Looking for conversations in: {json_path}")

        if not json_path.exists():
            messagebox.showwarning("No Data", "Please place conversation JSON files in the 'conversations' folder.")
            return

        self.json_files = list(json_path.glob("*.json"))
        if not self.json_files:
            messagebox.showwarning("No Files", "No JSON files found in the 'conversations' folder.")
            return

        print(f"Loaded {len(self.json_files)} JSON files from 'conversations' folder.")
        self.update_progress_label()
        self.update_progress_bar()
        self.load_conversation()

    def load_conversation(self):
        """
        Loads the current conversation and displays it.
        """
        if 0 <= self.current_file_index < len(self.json_files):
            try:
                with open(self.json_files[self.current_file_index], 'r', encoding='utf-8') as f:
                    self.current_data = json.load(f)
                print(f"Loaded conversation: {self.json_files[self.current_file_index].name}")
                self.display_conversation()
                self.update_progress_label()
                self.update_progress_bar()
            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Failed to load conversation due to JSON error: {str(e)}")
                print(f"JSON error: {str(e)}")
                self.next_conversation()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load conversation: {str(e)}")
                print(f"Error loading conversation: {str(e)}")
                self.next_conversation()
        else:
            messagebox.showinfo("Complete", "All conversations have been processed!")
            self.root.quit()

    def display_conversation(self):
        """
        Displays the conversation in the scrollable text widget with colored message bubbles.
        """
        self.conversation_text.configure(state='normal')
        self.conversation_text.delete('1.0', tk.END)

        # Clear existing tags
        for tag in self.conversation_text.tag_names():
            self.conversation_text.tag_delete(tag)

        if self.current_data and 'conversation_data' in self.current_data:
            for msg in self.current_data['conversation_data']:
                timestamp = msg.get('timestamp', 'No Timestamp')
                sender = msg.get('sender', 'No Sender')
                message = msg.get('message', 'No Message')

                # Assign a color to the sender if not already assigned
                if sender not in self.sender_colors:
                    if self.next_color_index < len(self.available_colors):
                        self.sender_colors[sender] = self.available_colors[self.next_color_index]
                        self.next_color_index += 1
                    else:
                        # Default color if all predefined colors are used
                        self.sender_colors[sender] = '#FFFFFF'

                color = self.sender_colors[sender]

                # Create a unique tag for the sender
                tag_name = f"sender_{sender}"
                self.conversation_text.tag_configure(tag_name, background=color, lmargin1=5, lmargin2=5, rmargin=5, spacing1=5, spacing3=5, wrap='word')

                # Insert the message with the tag
                formatted_message = f"{timestamp} - {sender}:\n{message}\n\n"
                self.conversation_text.insert(tk.END, formatted_message, tag_name)

            self.conversation_text.configure(state='disabled')
        else:
            print("No messages found in the current data.")

    def save_current(self):
        """
        Saves the current conversation's labeled data to the Excel file.
        """
        if not self.current_data:
            return

        conversation_id = self.json_files[self.current_file_index].stem

        # Load existing data
        try:
            df = pd.read_excel(self.output_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read the output file: {str(e)}")
            return

        # Remove existing entries for this conversation to prevent duplicates
        df = df[df['conversation_id'] != conversation_id]

        # Create new rows for each segment with filled data
        new_rows = []
        for segment in self.segments:
            mode = self.segment_mode_var.get()
            segment_index = self.segments.index(segment) + 1
            if segment_index > mode:
                continue

            sentiment = self.segment_vars[f"{segment}_sentiment_var"].get()
            engagement = self.segment_vars[f"{segment}_engagement_var"].get()
            customer_effort = self.segment_vars[f"{segment}_ces_var"].get()
            response_type = self.segment_vars[f"{segment}_response_type_var"].get()

            new_row = {
                'conversation_id': conversation_id,
                'segment': segment,
                'sentiment': sentiment if sentiment != 0 else None,
                'engagement_score': engagement if engagement != 0 else None,
                'customer_effort_score': customer_effort if customer_effort != 0 else None,
                'response_type': response_type if response_type != '' else None,
                # Add other fields as needed
            }
            new_rows.append(new_row)

        if new_rows:
            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            try:
                df.to_excel(self.output_file, index=False)
                print("Saved data successfully.")
                self.show_notification("Data saved successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save data: {str(e)}")

    def save_and_next(self):
        """
        Saves the current conversation's labeled data and moves to the next conversation.
        """
        self.save_current()
        self.next_conversation()

    def skip_current(self):
        """
        Skips the current conversation without saving and moves to the next.
        """
        if messagebox.askyesno("Skip Conversation", "Are you sure you want to skip this conversation?"):
            self.show_notification("Conversation skipped.")
            self.next_conversation()

    def next_conversation(self):
        """
        Moves to the next conversation in the list.
        """
        self.current_file_index += 1
        self.clear_form()
        if self.current_file_index >= len(self.json_files):
            messagebox.showinfo("Complete", "All conversations have been processed!")
            self.root.quit()
        else:
            self.load_conversation()

    def clear_form(self):
        """
        Clears all input fields for each segment.
        """
        for segment in self.segments:
            self.segment_vars[f"{segment}_sentiment_var"].set(0)  # Reset to no selection
            self.segment_vars[f"{segment}_engagement_var"].set(0)  # Reset to no selection
            self.segment_vars[f"{segment}_ces_var"].set(0)  # Reset customer effort to no selection
            self.segment_vars[f"{segment}_response_type_var"].set("")  # Reset response type to no selection

    def update_progress_label(self):
        """
        Updates the progress label to show the current conversation out of total.
        """
        total = len(self.json_files)
        current = self.current_file_index + 1 if total > 0 else 0
        self.progress_var.set(f"Conversation {current}/{total}")

    def update_progress_bar(self):
        """
        Updates the progress bar to reflect the current progress.
        """
        total = len(self.json_files)
        if total > 0:
            progress = ((self.current_file_index) / total) * 100
            self.progress_bar['value'] = progress
        else:
            self.progress_bar['value'] = 0

    def show_notification(self, message, duration=2):
        """
        Displays a transient notification that disappears after a specified duration.

        Args:
            message (str): The message to display.
            duration (int): Duration in seconds for which the notification is visible.
        """
        self.notification_label.config(text=message)
        self.notification_label.lift()  # Bring the notification to the front

        def hide_notification():
            time.sleep(duration)
            self.notification_label.config(text="")

        threading.Thread(target=hide_notification, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversationLabeler(root)
    root.mainloop()
