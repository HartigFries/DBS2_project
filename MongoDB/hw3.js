// ---------------------------------------------------------------------------------------------
// Task 1
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------

// Task 2
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------
// Task 3
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------
// Task 4
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------
// Task 5
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------
// Task 6
// ---------------------------------------------------------------------------------------------

db.posts.aggregate([
  {
    $match: {
      created_at: { $gte: ISODate("2022-10-01T00:00:00Z") },
      tags: { $ne: [] }
    }
  },
  { $unwind: "$tags" },
  {
    $group: {
      _id: "$tags",              // tagged user (ObjectId)
      tagCount: { $sum: 1 }
    }
  },
  { $sort: { tagCount: -1 } },
  { $limit: 10 },
  {
    $lookup: {
      from: "users",
      localField: "_id",         // ObjectId
      foreignField: "_id",
      as: "user"
    }
  },
  { $unwind: "$user" },
  {
    $project: {
      _id: 0,
      tagged_user_id: "$user.user_id",
      username: "$user.username",
      country: "$user.country",
      tagCount: 1
    }
  }
]);


// ---------------------------------------------------------------------------------------------
// Task 7
// ---------------------------------------------------------------------------------------------

db.posts.aggregate([
  {
    $match: {
      created_at: { $gte: ISODate("2022-12-02T00:00:00Z") },
      tags: { $ne: [] },
      group: { $ne: null }
    }
  },
  { $unwind: "$tags" },
  {
    $group: {
      _id: "$group",             // group ObjectId
      tagCount: { $sum: 1 }
    }
  },
  { $sort: { tagCount: -1 } },
  { $limit: 10 },
  {
    $lookup: {
      from: "groups",
      localField: "_id",
      foreignField: "_id",
      as: "group"
    }
  },
  { $unwind: "$group" },
  {
    $project: {
      _id: 0,
      group_id: "$group.group_id",
      group_name: "$group.name",
      tagCount: 1
    }
  }
]);


// ---------------------------------------------------------------------------------------------
// Task 8
// ---------------------------------------------------------------------------------------------

db.comments.aggregate([
  {
    $match: {
      written_at: { $gte: ISODate("2022-10-03T00:00:00Z") }
    }
  },
  {
    $lookup: {
      from: "posts",
      localField: "post",        // post ObjectId
      foreignField: "_id",
      as: "post"
    }
  },
  { $unwind: "$post" },
  {
    $lookup: {
      from: "users",
      localField: "post.user",   // creator of the post
      foreignField: "_id",
      as: "postCreator"
    }
  },
  { $unwind: "$postCreator" },
  {
    $match: {
      "postCreator.is_commercial": 1   // keep only ad posts
    }
  },
  {
    $group: {
      _id: "$user",                    // commenter ObjectId
      adEngagementCount: { $sum: 1 }
    }
  },
  { $sort: { adEngagementCount: -1 } },
  { $limit: 10 },
  {
    $lookup: {
      from: "users",
      localField: "_id",
      foreignField: "_id",
      as: "user"
    }
  },
  { $unwind: "$user" },
  {
    $project: {
      _id: 0,
      user_id: "$user.user_id",
      username: "$user.username",
      country: "$user.country",
      adEngagementCount: 1
    }
  }
]);


// ---------------------------------------------------------------------------------------------
// Task 12
// ---------------------------------------------------------------------------------------------

db.posts.aggregate([
  {
    $match: {
      activity: ObjectId("000000000000000000000032")   // activity 50
    }
  },
  {
    $group: {
      _id: "$user",           // user ObjectId
      attempts: { $sum: 1 },
      firstAttempt: { $min: "$created_at" },
      lastAttempt: { $max: "$created_at" }
    }
  },
  { $sort: { attempts: -1 } },
  {
    $lookup: {
      from: "users",
      localField: "_id",
      foreignField: "_id",
      as: "user"
    }
  },
  { $unwind: "$user" },
  {
    $project: {
      _id: 0,
      user_id: "$user.user_id",
      username: "$user.username",
      attempts: 1,
      firstAttempt: 1,
      lastAttempt: 1
    }
  }
]);


// ---------------------------------------------------------------------------------------------
// Task 14
// ---------------------------------------------------------------------------------------------

db.posts.aggregate([
  {
    $match: {
      activity: { $ne: null },
      created_at: { $gte: ISODate("2021-01-01T00:00:00Z") }
    }
  },
  {
    $lookup: {
      from: "activities",
      localField: "activity",
      foreignField: "_id",
      as: "activity"
    }
  },
  { $unwind: "$activity" },
  {
    $addFields: {
      month: { $month: "$created_at" }
    }
  },
  {
    $addFields: {
      season: {
        $switch: {
          branches: [
            { case: { $in: ["$month", [3, 4, 5]] }, then: "spring" },
            { case: { $in: ["$month", [6, 7, 8]] }, then: "summer" },
            { case: { $in: ["$month", [9, 10, 11]] }, then: "autumn" }
          ],
          default: "winter"
        }
      },
      weather: {
        $cond: [
          { $lt: ["$activity.base_elev_m", 300] }, "lowland",
          {
            $cond: [
              { $lt: ["$activity.base_elev_m", 800] }, "mid-altitude",
              "high-altitude"
            ]
          }
        ]
      }
    }
  },
  {
    $group: {
      _id: {
        activity_id: "$activity.activity_id",
        season: "$season",
        weather: "$weather"
      },
      attempts: { $sum: 1 },
      avg_distance_m: { $avg: "$activity.distance_m" },
      avg_total_elev_m: { $avg: "$activity.total_elev_m" }
    }
  },
  { $sort: { attempts: -1 } }
]);


// ---------------------------------------------------------------------------------------------
// Task 15
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------
// Task 16
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------
// Task 19
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------
// Task 20
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------
// Task 21
// ---------------------------------------------------------------------------------------------

// Code Here Pls

// ---------------------------------------------------------------------------------------------

