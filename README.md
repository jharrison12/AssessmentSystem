# AssessmentSystem
Assessment system created using the Django web framework

I divided the Assessment System app into two pages.  

<h2>/assessment/</h2>

The front-end page first asks the user to choose a semester, followed by a class followed by a student who is enrolled in that class.  After the user completes the rubric for the student, the user is taken back to the class page so the user can continue filling out rubrics for the course.  All rubrics must be completed in full before the user is allowed to submit.  

Based upon how the class is setup from the admin page, certain users (e.g. teachers) are only allowed to see certain classes.  This restriction ensures that users are not filling out rubrics for which they are not associated.

Accessing the /assessment/ page requires a login for the application

<h2>/data/</h2>

The application's data page gives the user two viewing options.  The first option allows the user to choose a student and then choose the course for which a professor or teacher has completed a rubric.  The second option allows the user to choose a semester and then choose class associated with that semester.  The class page will show aggregated rubric data and will show how many data points the aggregated rubric data represents. Access to the data view requires an administrative account.

<h2>/admin</h2>

The admin page, accessible by administrative user only, allows the user to create different models based upon the needs of the user.  The different models are below:

<h3>Ed class Semester</h3>

An itermediate model that allows a class to be associated with a particular semester.  This allows the user to change the rubric rather than particular being statically associated with a class

<h3>Ed classes</h3>

A model that represents a single entity of a class.  The class creation requires a unique identification number (i.e. crn), a subject, a course number (maximum four characters), a section number and a teacher associated with the course.  

<h3>Enrollment</h3>

An intermediate model that represents a particular students enrollment in a class and semester. "Rubriccompleted" indicates that the students rubric has been completed.  If the rubric needs to be edited after submission, you will need to disable rubric completed and resubmit the rubric.

<h3>Rubrics</h3>

The rubric model allows the user to create a rubric to be used for each course.  The rubric model consists of rows where the user can edit the name of the row and add descriptive text for each row/column intersection.  The user must enable the "Template" box to allow the rubric to be used in a course.  The template box differentiate's the blank rubric from a student's completed rubric (both based on the same model).  Rubric rows cannot be edited after creation except to add more rows.   

<h3>Semester</h3>

A model that represents a particular semester.

<h3>Students</h3>

A model that represents a student instance. The student model includes a first name, last name and a student identification number (i.e. Lnumber).  Student instances can be deleted or edited, but this is highly discouraged. 
