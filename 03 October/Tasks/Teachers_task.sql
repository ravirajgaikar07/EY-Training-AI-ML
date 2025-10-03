use university
db.teachers.insertMany([
  {name:"Pranita", department: "CS", salary: 25000},
  {name:"Rajesh",department:"AI",salary: 30000},
  {name:"Smita",department:"EC",salary:27000},
  {name:"Manoj",department:"IT",salary:26000}
])
{
  acknowledged: true,
  insertedIds: {
    '0': ObjectId('68dfb59a4422df82e0ba8c61'),
    '1': ObjectId('68dfb59a4422df82e0ba8c62'),
    '2': ObjectId('68dfb59a4422df82e0ba8c63'),
    '3': ObjectId('68dfb59a4422df82e0ba8c64')
  }
}
db.teachers.find()
{
  _id: ObjectId('68dfb59a4422df82e0ba8c61'),
  name: 'Pranita',
  department: 'CS',
  salary: 25000
}
{
  _id: ObjectId('68dfb59a4422df82e0ba8c62'),
  name: 'Rajesh',
  department: 'AI',
  salary: 30000
}
{
  _id: ObjectId('68dfb59a4422df82e0ba8c63'),
  name: 'Smita',
  department: 'EC',
  salary: 27000
}
{
  _id: ObjectId('68dfb59a4422df82e0ba8c64'),
  name: 'Manoj',
  department: 'IT',
  salary: 26000
}
db.teachers.find({salary : {$gt : 26000}})
{
  _id: ObjectId('68dfb59a4422df82e0ba8c62'),
  name: 'Rajesh',
  department: 'AI',
  salary: 30000
}
{
  _id: ObjectId('68dfb59a4422df82e0ba8c63'),
  name: 'Smita',
  department: 'EC',
  salary: 27000
}
db.teachers.find({},{name:1,department:1,_id:0})
{
  name: 'Pranita',
  department: 'CS'
}
{
  name: 'Rajesh',
  department: 'AI'
}
{
  name: 'Smita',
  department: 'EC'
}
{
  name: 'Manoj',
  department: 'IT'
}
db.teachers.updateMany({salary : 26000}, {$set : {salary:27000}})
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 1,
  modifiedCount: 1,
  upsertedCount: 0
}
db.teachers.updateMany({salary : {$lt : 27000}}, {$set : {salary:27000}})
{
  acknowledged: true,
  insertedId: null,
  matchedCount: 1,
  modifiedCount: 1,
  upsertedCount: 0
}
db.teachers.find()
{
  _id: ObjectId('68dfb59a4422df82e0ba8c61'),
  name: 'Pranita',
  department: 'CS',
  salary: 27000
}
{
  _id: ObjectId('68dfb59a4422df82e0ba8c62'),
  name: 'Rajesh',
  department: 'AI',
  salary: 30000
}
{
  _id: ObjectId('68dfb59a4422df82e0ba8c63'),
  name: 'Smita',
  department: 'EC',
  salary: 27000
}
{
  _id: ObjectId('68dfb59a4422df82e0ba8c64'),
  name: 'Manoj',
  department: 'IT',
  salary: 27000
}
db.teachers.deleteMany({department:"IT"})
{
  acknowledged: true,
  deletedCount: 1
}

