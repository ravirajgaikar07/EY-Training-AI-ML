use  university
db.students.insertOne({})
{
  acknowledged: true,
  insertedId: ObjectId('68dfa3ec749501096c57c8c1')
}
db.students.insertOne({
  student_id : 1,
  name : "Rahul",
  age : 21,
  city : "Mumbai",
  course : "AI",
  marks : 85
})
{
  acknowledged: true,
  insertedId: ObjectId('68dfa43f749501096c57c8c2')
}
db.students.insertMany([{student_id : 2, name: "Priya", age : 22, city : "Delhi", course: "ML", marks:90},
             {student_id : 3, name: "Arjun", age: 20, city : "Bengaluru", course: "DS",marks:78},
             {student_id : 4, name: "Neha", age: 23, city:"Hyderabad" , course: "AI",marks:88},
             {student_id : 4, name: "Vikram", age: 21,city:"Chennai",course:"ML",marks:95},
             {student_id : 5,name: "Yash",age: 22,city:"Pune",course:"AI",marks:80}])
{
  acknowledged: true,
  insertedIds: {
    '0': ObjectId('68dfa754749501096c57c8c3'),
    '1': ObjectId('68dfa754749501096c57c8c4'),
    '2': ObjectId('68dfa754749501096c57c8c5'),
    '3': ObjectId('68dfa754749501096c57c8c6'),
    '4': ObjectId('68dfa754749501096c57c8c7')
  }
}
db.students.find()
{
  _id: ObjectId('68dfa3ec749501096c57c8c1')
}
{
  _id: ObjectId('68dfa43f749501096c57c8c2'),
  student_id: 1,
  name: 'Rahul',
  age: 21,
  city: 'Mumbai',
  course: 'AI',
  marks: 85
}
{
  _id: ObjectId('68dfa754749501096c57c8c3'),
  student_id: 2,
  name: 'Priya',
  age: 22,
  city: 'Delhi',
  course: 'ML',
  marks: 90
}
{
  _id: ObjectId('68dfa754749501096c57c8c4'),
  student_id: 3,
  name: 'Arjun',
  age: 20,
  city: 'Bengaluru',
  course: 'DS',
  marks: 78
}
{
  _id: ObjectId('68dfa754749501096c57c8c5'),
  student_id: 4,
  name: 'Neha',
  age: 23,
  city: 'Hyderabad',
  course: 'AI',
  marks: 88
}
{
  _id: ObjectId('68dfa754749501096c57c8c6'),
  student_id: 4,
  name: 'Vikram',
  age: 21,
  city: 'Chennai',
  course: 'ML',
  marks: 95
}
{
  _id: ObjectId('68dfa754749501096c57c8c7'),
  student_id: 5,
  name: 'Yash',
  age: 22,
  city: 'Pune',
  course: 'AI',
  marks: 80
}
db.students.findOne({name: "Rahul"})
{
  _id: ObjectId('68dfa43f749501096c57c8c2'),
  student_id: 1,
  name: 'Rahul',
  age: 21,
  city: 'Mumbai',
  course: 'AI',
  marks: 85
}
db.students.find({marks : {$gt : 85}})
{
  _id: ObjectId('68dfa754749501096c57c8c3'),
  student_id: 2,
  name: 'Priya',
  age: 22,
  city: 'Delhi',
  course: 'ML',
  marks: 90
}
{
  _id: ObjectId('68dfa754749501096c57c8c5'),
  student_id: 4,
  name: 'Neha',
  age: 23,
  city: 'Hyderabad',
  course: 'AI',
  marks: 88
}
{
  _id: ObjectId('68dfa754749501096c57c8c6'),
  student_id: 4,
  name: 'Vikram',
  age: 21,
  city: 'Chennai',
  course: 'ML',
  marks: 95
}
db.students.find({},{name:1,course:1,_id:0})
{}
{
  name: 'Rahul',
  course: 'AI'
}
{
  name: 'Priya',
  course: 'ML'
}
{
  name: 'Arjun',
  course: 'DS'
}
{
  name: 'Neha',
  course: 'AI'
}
{
  name: 'Vikram',
  course: 'ML'
}
{
  name: 'Yash',
  course: 'AI'
}
db.students.updateOne({name: "Neha"},{$set : {city : "Delhi", marks : 86}})
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 1,
  modifiedCount: 1,
  upsertedCount: 0
}
db.students.findOne({name:"Neha"})
{
  _id: ObjectId('68dfa754749501096c57c8c5'),
  student_id: 4,
  name: 'Neha',
  age: 23,
  city: 'Delhi',
  course: 'AI',
  marks: 86
}
db.students.updateMany({course:"AI"},{$set:{grade : "A"}})
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 3,
  modifiedCount: 3,
  upsertedCount: 0
}
db.students.find()
{
  _id: ObjectId('68dfa3ec749501096c57c8c1')
}
{
  _id: ObjectId('68dfa43f749501096c57c8c2'),
  student_id: 1,
  name: 'Rahul',
  age: 21,
  city: 'Mumbai',
  course: 'AI',
  marks: 85,
  grade: 'A'
}
{
  _id: ObjectId('68dfa754749501096c57c8c3'),
  student_id: 2,
  name: 'Priya',
  age: 22,
  city: 'Delhi',
  course: 'ML',
  marks: 90
}
{
  _id: ObjectId('68dfa754749501096c57c8c4'),
  student_id: 3,
  name: 'Arjun',
  age: 20,
  city: 'Bengaluru',
  course: 'DS',
  marks: 78
}
{
  _id: ObjectId('68dfa754749501096c57c8c5'),
  student_id: 4,
  name: 'Neha',
  age: 23,
  city: 'Delhi',
  course: 'AI',
  marks: 86,
  grade: 'A'
}
{
  _id: ObjectId('68dfa754749501096c57c8c6'),
  student_id: 4,
  name: 'Vikram',
  age: 21,
  city: 'Chennai',
  course: 'ML',
  marks: 95
}
{
  _id: ObjectId('68dfa754749501096c57c8c7'),
  student_id: 5,
  name: 'Yash',
  age: 22,
  city: 'Pune',
  course: 'AI',
  marks: 80,
  grade: 'A'
}
db.students.deleteOne({name:"Yash"})
{
  acknowledged: true,
  deletedCount: 1
}
db.students.deleteMany({marks : {$lt : 80}})
{
  acknowledged: true,
  deletedCount: 1
}