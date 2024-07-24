# src/views/dashboard_tab.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtGui import QPainter
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from io import BytesIO
from PySide6.QtGui import QPixmap

class DashboardTab(QWidget):
    def __init__(self, email_accounts):
        super().__init__()
        self.email_accounts = email_accounts
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Email account statistics
        account_stats_layout = QHBoxLayout()
        account_stats_layout.addWidget(QLabel(f"Email Accounts Monitored: {len(self.email_accounts)}"))
        layout.addLayout(account_stats_layout)

        # Email flag statistics
        flag_stats_layout = QHBoxLayout()
        self.urgent_label = QLabel("Urgent: 0")
        self.important_label = QLabel("Important: 0")
        self.on_track_label = QLabel("On Track: 0")
        self.unmarked_label = QLabel("Unmarked: 0")
        flag_stats_layout.addWidget(self.urgent_label)
        flag_stats_layout.addWidget(self.important_label)
        flag_stats_layout.addWidget(self.on_track_label)
        flag_stats_layout.addWidget(self.unmarked_label)
        layout.addLayout(flag_stats_layout)

        # Unique senders list
        layout.addWidget(QLabel("Unique Senders:"))
        self.senders_list = QListWidget()
        layout.addWidget(self.senders_list)

        # Pie chart for email flags
        self.chart_view = QChartView()
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        layout.addWidget(self.chart_view)

        # Word cloud for email subjects
        self.word_cloud_label = QLabel()
        layout.addWidget(self.word_cloud_label)

        self.setLayout(layout)

    def update_dashboard(self, emails):
        # Update flag statistics
        flag_counts = Counter(email.get('flag', 'unmarked') for email in emails)
        self.urgent_label.setText(f"Urgent: {flag_counts['red']}")
        self.important_label.setText(f"Important: {flag_counts['orange']}")
        self.on_track_label.setText(f"On Track: {flag_counts['green']}")
        self.unmarked_label.setText(f"Unmarked: {flag_counts['grey']}")

        # Update unique senders list
        unique_senders = set(email['sender'] for email in emails)
        self.senders_list.clear()
        self.senders_list.addItems(sorted(unique_senders))

        # Update pie chart
        series = QPieSeries()
        series.append("Urgent", flag_counts['red'])
        series.append("Important", flag_counts['orange'])
        series.append("On Track", flag_counts['green'])
        series.append("Unmarked", flag_counts['grey'])

        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Email Flags Distribution")
        self.chart_view.setChart(chart)

        # Update word cloud
        subject_text = ' '.join(email['subject'] for email in emails)
        wordcloud = WordCloud(width=400, height=200, background_color='white').generate(subject_text)
        
        plt.figure(figsize=(5, 2.5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image = QPixmap()
        image.loadFromData(buffer.getvalue())
        self.word_cloud_label.setPixmap(image)
        plt.close()

    def reset(self):
        self.senders_list.clear()
        self.urgent_label.setText("Urgent: 0")
        self.important_label.setText("Important: 0")
        self.on_track_label.setText("On Track: 0")
        self.unmarked_label.setText("Unmarked: 0")
        self.chart_view.chart().removeAllSeries()
        self.word_cloud_label.clear()