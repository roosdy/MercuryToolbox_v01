# Mercury Toolbox

## Overview

Mercury Toolbox is a user-friendly email management and communication tool designed to enhance productivity and streamline your email workflow. With features like AI-powered email summarization, customizable email categorization, and an intuitive dashboard, Mercury provides a comprehensive solution for efficient email management, while prioritizing enterprise safety and data protection.

## Features

### Email Management
- **Multi-account Support**: Manage multiple email accounts from a single interface.
- **Email Fetching**: Quickly fetch and display recent emails from your accounts.
- **Email Categorization**: Mark emails with four different flags (Urgent, Important, On Track, Unmarked) for easy prioritization.
- **Email Content Display**: View both summarized and full email content.

### AI-Powered Summarization
- **Smart Summaries**: Utilize OpenAI's GPT-4o-mini model to generate concise bullet-point summaries of email content.
- **Batch Summarization**: Summarize multiple selected emails at once.

### Dashboard
- **Email Statistics**: View at-a-glance statistics about your email accounts and messages.
- **Unique Sender List**: Keep track of all unique senders in your inbox.
- **Flag Distribution**: Visualize the distribution of email flags with an interactive pie chart.
- **Keyword Analysis**: Identify common keywords in your email subjects through a word cloud visualization.

### Chatbot Assistant
- **AI-Powered Chat**: Interact with an AI assistant for additional help and information.

### User Interface
- **Tabbed Interface**: Navigate easily between different functionalities with a clean, tabbed interface.
- **System Tray Integration**: Keep the application running in the background for quick access.

### Security and Customization
- **Secure Connections**: Handle secure connections to email servers.
- **Customizable Settings**: Set up and manage email accounts and preferences.


## Enterprise Safety and Security

Mercury Toolbox is designed with enterprise-grade security in mind. We implement the following best practices to ensure the safety and integrity of your data:

### Data Protection
- **End-to-End Encryption**: All data transmissions are encrypted using industry-standard protocols.
- **Local Data Storage**: Email data is stored locally on the user's machine, minimizing cloud-based vulnerabilities.
- **Secure Authentication**: Multi-factor authentication (MFA) is supported for accessing email accounts.

### Privacy Compliance
- **GDPR Compliance**: Our data handling practices are in line with GDPR requirements for EU users.
- **Data Minimization**: We only collect and process data that is necessary for the functioning of the application.
- **User Consent**: Clear consent is obtained for any data processing activities.

### AI Ethics and Safety
- **AI Model Isolation**: The AI summarization feature uses isolated environments to prevent data leakage.
- **No Data Retention**: AI-generated summaries are not stored or used for model training.
- **Transparency**: Users are always informed when AI-generated content is being displayed.

### Enterprise Integration
- **Active Directory Support**: Seamlessly integrate with your organization's Active Directory for user management.
- **Audit Logging**: Comprehensive logging of all system activities for security audits.
- **Role-Based Access Control (RBAC)**: Granular control over user permissions and feature access.

### Regulatory Compliance
- **Configurable Data Retention**: Set up data retention policies in compliance with your industry regulations.
- **Export and Deletion**: Easy-to-use tools for exporting user data and permanent deletion upon request.

## Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- OpenSSL 1.1.1 or higher

### Steps
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/communications-toolbox.git
   cd communications-toolbox
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key securely:
   - Create a `.env` file in the project root directory.
   - Add your OpenAI API key to the file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```
   - Ensure the `.env` file is added to your `.gitignore` to prevent accidental exposure.

5. Configure enterprise settings:
   - Copy `config/enterprise_config.example.yaml` to `config/enterprise_config.yaml`
   - Modify the settings in `enterprise_config.yaml` according to your organization's policies

## Usage

1. Run the application:
   ```
   python src/main.py
   ```

2. Add your email accounts:
   - Click on the "Add Email Account" button in the Email tab.
   - Enter your email address, password, and server details.

3. Fetch emails:
   - Select an account from the list and click "Fetch Emails".

4. Manage emails:
   - View email content by clicking on an email in the list.
   - Categorize emails using the right-click context menu.
   - Summarize selected emails using the "Summarize Selected Emails" button.

5. View dashboard:
   - Switch to the Dashboard tab to see email statistics and visualizations.

6. Use the chatbot:
   - Navigate to the Chatbot tab for AI-assisted support.


## Security Best Practices

1. **Regular Updates**: Keep the application and all its dependencies up to date to ensure you have the latest security patches.

2. **Network Security**: Use the application within a secure, firewalled network environment.

3. **Access Control**: Implement strict access controls and regularly audit user access.

4. **Data Backups**: Regularly backup your data and test restoration procedures.

5. **Security Training**: Ensure all users undergo security awareness training before using the application.

6. **Incident Response Plan**: Have a clear incident response plan in place for potential security breaches.

7. **Third-Party Audits**: Conduct regular third-party security audits of the application deployment.

## Compliance

Mercury Toolbox is designed to help your organization maintain compliance with various regulatory requirements. However, compliance is a shared responsibility. Ensure you configure and use the application in accordance with your specific compliance needs.

- **GDPR**: Configurable data retention and deletion features support GDPR compliance.
- **HIPAA**: When properly configured, can be used as part of a HIPAA-compliant email workflow.
- **SOC 2**: Supports the security and availability principles of SOC 2 compliance.

Always consult with your legal and compliance teams to ensure proper use and configuration.

## Contributing

We welcome contributions to the Mercury Toolbox project! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to submit contributions. All contributions will undergo security review before acceptance.

## License

This project is licensed under the MIT License. See the [LICENSE](https://opensource.org/license/mit) file for details.

## Support and Reporting Security Issues

For general support, please contact our support team at roosdy@roosdy.dev

To report security vulnerabilities or for other security-related issues, please email roosdy@roosdy.dev. 
We treat all security issues with the highest priority.

## Acknowledgments

- OpenAI for GPT-4o-mini model used in email summarization.
- The PySide6 team for the excellent Qt framework for Python.
- All contributors and users of Mercury Toolbox.