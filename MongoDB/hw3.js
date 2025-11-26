db.users.insertMany([
        {
            _id: 99001,
            username: "Alice Commercial (CZ)",
            country: "cz",
            join_date: ISODate("2020-01-10T00:00:00Z"),
            joined_groups: [{ group_id: 99001, joined_at: ISODate("2020-01-12T00:00:00Z") }],
            created_posts: [ 99001 ],
            is_commercial: 1
        },
        {
            _id: 99002,
            username: "Bob Newbie (US)",
            country: "us",
            join_date: ISODate("2022-11-15T10:00:00Z"),
            joined_groups: [{ group_id: 99002, joined_at: ISODate("2022-11-16T10:00:00Z") }],
            created_posts: [ 99002 ],
            is_commercial: 0
        },
        {
            _id: 99003,
            username: "Charlie Inactive (DE)",
            country: "de",
            join_date: ISODate("2022-12-05T10:00:00Z"),
            joined_groups: [],
            created_posts: [],
            is_commercial: 0
        }
    ]);

db.groups.insertMany([
        {
            _id: 99001,
            name: "Dead Group CZ",
            country: "cz",
            posts: [ 99001 ],
            last_activity: ISODate("2022-10-01T00:00:00Z")
        },
        {
            _id: 99002,
            name: "Active Group US",
            country: "us",
            posts: [ 99002 ],
            last_activity: ISODate("2022-12-20T00:00:00Z")
        }
    ]);

db.activities.insertMany([
        {
            _id: 50,
            region: "Sumava", country: "cz", distance_m: 15000, base_elev_m: 800, total_elev_m: 1200
        },
        {
            _id: 99002, region: "Grand Canyon", country: "us", distance_m: 5000, base_elev_m: 200, total_elev_m: 100
        }
    ]);

db.posts.insertMany([
        {
            _id: 99001,
            text: "Commercial Post in October",
            created_at: ISODate("2022-10-15T14:00:00Z"),
            tags: [ 99002 ],
            group: 99001,
            user: 99001,
            activity: null
        },
        {
            _id: 99002,
            text: "Onboarding Post",
            created_at: ISODate("2022-11-17T09:00:00Z"),
            tags: [],
            group: 99002,
            user: 99002,

            activity: ObjectId("000000000000000000000032")
        },
        {
            _id: 99003,
            text: "December Group Post",
            created_at: ISODate("2022-12-05T18:30:00Z"),
            tags: [ 99001 ],
            group: 99002,
            user: 99002,
            activity: 50
        }
    ]);


db.comments.insertMany([
        {
            _id: 99001,
            user_id: 99003,
            post_id: 99001, /
            written_at: ISODate("2022-10-16T10:00:00Z")
        }
    ]);

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

db.users.createIndex({ join_date: 1 });
db.posts.createIndex({ created_at: 1 });

var startDate = ISODate("2022-11-01T00:00:00Z");
var endDate = ISODate("2022-12-31T23:59:59Z");

db.users.aggregate([
    {
        $match: {
            join_date: { $gte: startDate, $lt: endDate }
        }
    },
    { $limit: 20 },
    {
        $addFields: {
            deadline: { $add: ["$join_date", 7 * 24 * 60 * 60 * 1000] }
        }
    },
    {
        $addFields: {
            joined_first_group: {
                $gt: [
                    {
                        $size: {
                            $filter: {
                                input: "$joined_groups",
                                as: "g",
                                cond: { $lte: ["$$g.joined_at", "$deadline"] }
                            }
                        }
                    }, 0
                ]
            }
        }
    },
    {
        $lookup: {
            from: "posts",
            localField: "created_posts",
            foreignField: "_id",
            as: "post_details"
        }
    },
    {
        $addFields: {
            completed_first_share: {
                $gt: [
                    {
                        $size: {
                            $filter: {
                                input: "$post_details",
                                as: "p",
                                cond: { $lte: ["$$p.created_at", "$deadline"] }
                            }
                        }
                    }, 0
                ]
            }
        }
    },
    {
        $project: {
            _id: 0,
            username: 1,
            join_date: 1,
            country: 1,
            completed_first_share: 1,
            joined_first_group: 1
        }
    },
    { $sort: { join_date: 1 } }

]).forEach(printjson);

// ---------------------------------------------------------------------------------------------
// Task 16
// ---------------------------------------------------------------------------------------------

db.posts.createIndex({ created_at: 1 });
db.comments.createIndex({ written_at: 1 });

var referenceDate = ISODate("2022-12-31T23:59:59Z");
var startDate = new Date(referenceDate - 90 * 24 * 60 * 60 * 1000);

db.posts.aggregate([
    {
        $match: {
            created_at: { $gte: startDate, $lte: referenceDate }
        }
    },
    {
        $project: { timestamp: "$created_at", type: "post" }
    },
    {
        $unionWith: {
            coll: "comments",
            pipeline: [
                { $match: { written_at: { $gte: startDate, $lte: referenceDate } } },
                { $project: { timestamp: "$written_at", type: "comment" } }
            ]
        }
    },
    {
        $project: {
            day: { $dayOfWeek: "$timestamp" },
            hour: { $hour: "$timestamp" }
        }
    },
    {
        $group: {
            _id: { day: "$day", hour: "$hour" },
            total_interactions: { $sum: 1 }
        }
    },
    { $sort: { total_interactions: -1 } },
    { $limit: 5 },
    {
        $project: {
            _id: 0,
            day_of_week: "$_id.day",
            hour_of_day: "$_id.hour",
            total_interactions: 1
        }
    }

]).forEach(printjson);

// ---------------------------------------------------------------------------------------------
// Task 19
// ---------------------------------------------------------------------------------------------

db.users.createIndex({ country: 1 });
db.activities.createIndex({ country: 1 });

db.users.aggregate([

    {
        $group: {
            _id: "$country",
            userCount: { $sum: 1 }
        }
    },
    {
        $lookup: {
            from: "activities",
            localField: "_id",
            foreignField: "country",
            as: "paths_in_region"
        }
    },
    {
        $project: {
            region: "$_id",
            active_users: "$userCount",
            path_count: { $size: "$paths_in_region" },
            _id: 0
        }
    },
    {
        $project: {
            region: 1,
            active_users: 1,
            path_count: 1,
            user_to_path_ratio: {
                $cond: {
                    if: { $eq: ["$path_count", 0] },
                    then: 0,
                    else: { $divide: ["$active_users", "$path_count"] }
                }
            }
        }
    },
    { $sort: { user_to_path_ratio: -1 } },
    { $limit: 10 }

]).forEach(printjson);

// ---------------------------------------------------------------------------------------------
// Task 20
// ---------------------------------------------------------------------------------------------

db.users.createIndex({ join_date: 1 });

var referenceDate = ISODate("2023-01-01T00:00:00Z");
var startDate = new Date(referenceDate - 90 * 24 * 60 * 60 * 1000);

db.users.aggregate([
    {
        $match: {
            join_date: { $gte: startDate, $lte: referenceDate }
        }
    },
    {
        $project: {
            step1_registered: { $literal: 1 },

            step2_joined: {
                $cond: [{ $gt: [{ $size: "$joined_groups" }, 0] }, 1, 0]
            },
            step3_posted: {
                $cond: [{ $gt: [{ $size: "$created_posts" }, 0] }, 1, 0]
            }
        }
    },
    {
        $group: {
            _id: null,
            total_reg: { $sum: "$step1_registered" },
            total_join: { $sum: "$step2_joined" },
            total_post: { $sum: "$step3_posted" }
        }
    },
    {
        $project: {
            _id: 0,
            steps: [
                {
                    step: "1. Registered",
                    count: "$total_reg",
                    rate: "100%"
                },
                {
                    step: "2. Joined First Group",
                    count: "$total_join",
                    rate: {
                        $concat: [
                            { $toString: { $multiply: [{ $divide: ["$total_join", "$total_reg"] }, 100] } },
                            "%"
                        ]
                    }
                },
                {
                    step: "3. Created First Post",
                    count: "$total_post",
                    rate: {
                        $concat: [
                            { $toString: { $multiply: [{ $divide: ["$total_post", "$total_reg"] }, 100] } },
                            "%"
                        ]
                    }
                }
            ]
        }
    },
    { $unwind: "$steps" },
    { $replaceRoot: { newRoot: "$steps" } }
]).forEach(printjson);

// ---------------------------------------------------------------------------------------------
// Task 21
// ---------------------------------------------------------------------------------------------

db.groups.createIndex({ last_activity: 1 });

var referenceDate = ISODate("2023-01-01T00:00:00Z");
var thresholdDate = new Date(referenceDate - 60 * 24 * 60 * 60 * 1000);

db.groups.aggregate([
    {
        $match: {
            last_activity: { $lt: thresholdDate }
        }
    },
    {
        $lookup: {
            from: "users",
            localField: "_id",
            foreignField: "joined_groups.group_id",
            as: "members"
        }
    },
    {
        $project: {
            _id: 0,
            group_id: "$_id",
            group_name: "$name",
            member_count: { $size: "$members" },

            days_since_last_activity: {
                $floor: {
                    $divide: [
                        { $subtract: [referenceDate, "$last_activity"] },
                        1000 * 60 * 60 * 24
                    ]
                }
            }
        }
    },
    { $sort: { days_since_last_activity: -1 } }
]).forEach(printjson);

// ---------------------------------------------------------------------------------------------

