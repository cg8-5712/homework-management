# Homework Management System

A comprehensive web-based system for managing student homework submissions, teacher reviews, and class representative oversight.

## Features

### Multi-Role Support
- **Students:** Submit homework and view feedback
- **Teachers:** Review submissions and provide feedback
- **Class Representatives:** Monitor submissions and export statistics
- **Administrators:** System monitoring and log review

### Key Functionalities
- Secure file upload for homework submissions
- Real-time submission status tracking
- Interactive image preview
- Batch homework management
- Excel export for submission statistics
- System activity logging

## Technical Stack

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Data Storage:** JSON-based file system
- **File Handling:** Werkzeug
- **Export Support:** SheetJS

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd homework_management
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
- Set up `users.json` with user credentials
- Create necessary directories:
  ```bash
  mkdir static/uploads
  ```

4. Run the application:
```bash
python app.py
```

## Project Structure

```
homework_management/
├── app.py                 # Main application file
├── templates/            # HTML templates
│   ├── admin_dashboard.html
│   ├── class_rep_manage.html
│   ├── index.html
│   ├── login.html
│   ├── submit_homework.html
│   ├── teacher_review.html
│   ├── teacher_review_reply.html
│   └── view_homework.html
├── static/              # Static files
│   └── uploads/         # Homework submissions
├── users.json           # User data
└── homework_data.json   # Homework records
```

## Usage

### Student Interface
- Login with student credentials
- View available homework assignments
- Submit homework files with comments
- View teacher feedback

### Teacher Interface
- Review student submissions
- Provide feedback
- View submission statistics
- Manage homework assignments

### Class Representative Tools
- Monitor submission status
- Export submission statistics
- Switch between student/manager views
- Generate reports

### Admin Dashboard
- Monitor system activity
- View detailed logs
- Track user actions

## Security Features

- Secure file upload handling
- Role-based access control
- Session management
- Input validation
- Secure file storage

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## Version History

### v1.1.5
- Added homework content display
- Implemented class representative Excel export
- Enhanced user experience
- Bug fixes and performance improvements

## License

This project is licensed under the GPLV3 License - see the LICENSE file for details.